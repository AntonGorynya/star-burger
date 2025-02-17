# Generated by Django 3.2.15 on 2023-08-15 13:36

import django.core.validators
from django.db import migrations, models


def set_price(apps, schema_editors):
    Cart = apps.get_model('foodcartapp', 'Cart')
    for cart in Cart.objects.all().iterator():
        cart.fixed_price = cart.quantity * cart.product.price
        cart.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_address_cart_customer_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='fixed_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
            preserve_default=False,
        ),
        migrations.RunPython(set_price),
    ]
