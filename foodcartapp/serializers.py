import datetime
import requests

from requests.exceptions import HTTPError, Timeout, ConnectionError
from star_burger.settings import YANDEX_KEY
from rest_framework.serializers import ValidationError, ModelSerializer
from .models import Product, Customer, Address, OrderedProduct, Order


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ['address']

    def create(self, validated_data):
        print('Create address')
        print(validated_data['address'])
        address = validated_data['address']
        coordinates = fetch_coordinates(YANDEX_KEY, address)
        address, _ = Address.objects.get_or_create(
            address=address,
            lat=coordinates['lat'],
            lon=coordinates['lon'],
        )
        return address


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ['firstname', 'lastname', 'phonenumber']

    def create(self, validated_data, address):
        print('creating customer')
        print(validated_data)
        customer, _ = Customer.objects.get_or_create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=address
        )
        return customer


class OrderedProductSerializer(ModelSerializer):
    class Meta:
            model = OrderedProduct
            fields = ['product', 'quantity']

    def create(self, validated_data, order):
        print('creating products')
        print(validated_data)
        for product in validated_data:
            OrderedProduct.objects.get_or_create(
                product=product['product'],
                quantity=product['quantity'],
                order=order,
                fixed_price=product['quantity']*product['product'].price
            )


class OrderSerializer(ModelSerializer):
    address = AddressSerializer(many=False)
    customer = CustomerSerializer(many=False)
    products = OrderedProductSerializer(many=True)

    def validate_products(self, value):
        print('validate_products')
        print(value)
        if not value:
            raise ValidationError('Empty product list')
        return value

    def create(self, validated_data):
        address = AddressSerializer.create(self, validated_data=validated_data['address'])
        customer = CustomerSerializer.create(self, validated_data=validated_data['customer'], address=address)
        order, _ = Order.objects.get_or_create(
            customer=customer,
            address=address,
            start_date=datetime.datetime.now(),
            end_date=None,
        )
        OrderedProductSerializer.create(self, validated_data=validated_data['products'], order=order)
        return address, customer, order

    class Meta:
        model = Order
        fields = ['address', 'customer', 'products']

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
    except (HTTPError, Timeout, ConnectionError):
        return {'lon': None, 'lat': None}
