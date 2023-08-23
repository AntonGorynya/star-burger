import logging

from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from environs import Env

from .models import Product
from .serializers import OrderSerializer

env = Env()
env.read_env()
yandex_key = env('YANDEX_KEY')
logger = logging.getLogger('foodcartapp')
logger.setLevel(logging.DEBUG)


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
    customer = {}
    web_order = request.data
    customer['firstname'] = web_order.pop('firstname')
    customer['lastname'] = web_order.pop('lastname')
    customer['phonenumber'] = web_order.pop('phonenumber')
    web_order['address'] = {'address': web_order['address']}
    web_order['customer'] = customer
    print('web_order\n', web_order)
    logging.info(web_order)

    serializer = OrderSerializer(data=web_order)
    serializer.is_valid()
    logging.debug(serializer.errors)
    print('errors\n', serializer.errors)
    logging.debug(serializer.validated_data)
    print('data\n', serializer.validated_data)

    address, customer, order = serializer.create(serializer.validated_data)

    context = {
        'id': order.id,
        'firstname': customer.firstname,
        'lastname': customer.lastname,
        'phonenumber': str(customer.phonenumber),
        'address': address.address
    }
    print(f'context:\n{context}')
    return Response(context)
