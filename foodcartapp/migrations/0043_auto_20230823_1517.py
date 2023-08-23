# Generated by Django 3.2.15 on 2023-08-23 12:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_alter_restaurant_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100)], verbose_name='количество')),
                ('fixed_price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена за штуку')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='foodcartapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='foodcartapp.product', verbose_name='Товар')),
            ],
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
    ]
