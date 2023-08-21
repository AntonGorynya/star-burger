import datetime
import requests

from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError, Serializer, ModelSerializer, CharField, ListField
from environs import Env

from .models import Product, Customer, Address, Cart, Order

env = Env()
env.read_env()
yandex_key = env('YANDEX_KEY')


class CartSerializer(ModelSerializer):
    class Meta:
            model = Cart
            fields = ['product', 'quantity']



class OrderSerializer(ModelSerializer):
    address = CharField()
    products = ListField()

    def validate_products(self, value):
        if not value:
            raise ValidationError('Empty product list')
        serializer = CartSerializer(many=True, data=value)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    class Meta:
        model = Customer
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


def fetch_coordinates(apikey, address):
    try:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return {'lon': None, 'lat': None}

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return {'lon': lon, 'lat': lat}
    except requests.exceptions.RequestException:
        return {'lon': None, 'lat': None}


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    web_order = request.data
    serializer = OrderSerializer(data=web_order)
    serializer.is_valid(raise_exception=True)

    products = serializer.validated_data['products']
    firstname = serializer.validated_data['firstname']
    lastname = serializer.validated_data['lastname']
    address = serializer.validated_data['address']
    phonenumber = PhoneNumber.from_string(serializer.validated_data['phonenumber'] )
    coordinates = fetch_coordinates(yandex_key, address)

    address, _ = Address.objects.get_or_create(
        address=address,
        lat=coordinates['lat'],
        lon=coordinates['lon'],
    )
    customer, _ = Customer.objects.get_or_create(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address
    )
    order, _ = Order.objects.get_or_create(
        customer=customer,
        address=address,
        start_date=datetime.datetime.now(),
        end_date=None,
    )
    for product in products:
        Cart.objects.get_or_create(
            product=product['product'],
            quantity=product['quantity'],
            order=order,
            fixed_price=product['quantity']*product['product'].price
        )
    context = {
        'id': order.id,
        'firstname': customer.firstname,
        'lastname': customer.lastname,
        'phonenumber': str(customer.phonenumber),
        'address': address.address
    }
    return Response(context)
