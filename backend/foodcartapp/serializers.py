import datetime
from .geo_tools import fetch_coordinates
from backend.star_burger.settings import YANDEX_KEY
from rest_framework.serializers import ModelSerializer
from .models import Customer, Address, OrderedProduct, Order


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ['address']

    def create(self, validated_data):
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
    products = OrderedProductSerializer(many=True, allow_empty=False)

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
