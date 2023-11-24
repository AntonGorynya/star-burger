# Generated by Django 3.2.15 on 2023-08-16 14:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_cart_fixed_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('MR', 'manager'), ('RN', 'restoran'), ('DY', 'delivery')], default='MR', max_length=2),
        ),
        migrations.AlterField(
            model_name='cart',
            name='fixed_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена за штуку'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='foodcartapp.product', verbose_name='Товар'),
        ),
        migrations.AlterField(
            model_name='order',
            name='end_date',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='Дата завершения заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='end_time',
            field=models.TimeField(blank=True, db_index=True, null=True, verbose_name='Время завершения заказа'),
        ),
    ]