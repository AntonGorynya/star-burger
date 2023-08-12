import datetime
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.templatetags.static import static
from django.core.exceptions import BadRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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


@api_view(['POST'])
def register_order(request):    
    try:
        web_order = request.data
        products = web_order['products']
        if not products:
            raise KeyError
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
        return Response(web_order)        
   
    except KeyError as err:
        return Response('Mandatory parametr not  found', status=status.HTTP_400_BAD_REQUEST)
    except TypeError as err:
        return Response('Value error', status=status.HTTP_400_BAD_REQUEST)
