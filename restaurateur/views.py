from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from geopy.distance import distance

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, Cart, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def distance_calculate(customer_place, restaurant_address):
    if None not in customer_place:
        return round(distance(customer_place, (restaurant_address.lat, restaurant_address.lon)).km)
    return None


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_actual_orders()
    context = {'orders': []}
    for order in orders:
        cart = order.cart.select_related('product')
        products = cart.values('product').distinct()
        customer_place = (order.address.lat, order.address.lon)

        restaurants = []
        if not order.restaurant:
            restaurants = Restaurant.objects.all()
            for product in products:
                menus = RestaurantMenuItem.objects.filter(product=product['product'])
                restaurants = restaurants.filter(menu_items__in=menus)
            restaurants = [
                {
                    'name': restaurant,
                    'distance': distance_calculate(customer_place, restaurant.address)
                } for restaurant in restaurants
            ]

        context['orders'].append({
            'id': order.id,
            'customer_name': f'{order.customer.firstname} {order.customer.lastname}',
            'phonenumber': order.customer.phonenumber,
            'address': order.address,
            'sum': cart.get_price(),
            'comments': order.comments,
            'restaurants': restaurants,
            'chosed_restaurant': order.restaurant,
            'status': order.get_status_display(),
        })

    return render(request, template_name='order_items.html', context=context)
