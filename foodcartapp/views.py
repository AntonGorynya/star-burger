import datetime
import json
from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Customer, Address, Cart, Order


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


def register_order(request):
    web_order = json.loads(request.body) 
    if web_order['products']:
        products = web_order['products']
        firstname = web_order['firstname']
        lastname = web_order['lastname']
        phonenumber = web_order['phonenumber']        

        address, _ = Address.objects.get_or_create(address=web_order['address'])
        customer, _ = Customer.objects.get_or_create(
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
            address=address
        )
        order, _ = Order.objects.get_or_create(
            customer=customer,
            address=address,
            start_date=datetime.datetime.now().date(),
            start_time=datetime.datetime.now().time(),
            end_date=None,
            end_time=None
        )
        for product in products:
            Cart.objects.get_or_create(
                product=Product.objects.get(id=product['product']),
                quantity=product['quantity'],
                order=order
            )



       
    return JsonResponse(web_order)
