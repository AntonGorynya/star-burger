from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class CartQuerySet(models.QuerySet):
    def get_price(self,  *args, **kwargs):
        #print(sum([item.quantity*item.product.price for item in self]))
        return self.aggregate(total=Sum(F('quantity')*F('product__price')))['total']


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Address(models.Model):
    address = models.CharField('Адрес', max_length=50)

    def __str__(self):
        return f'{self.address}'


class Customer(models.Model):
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона')
    address = models.ForeignKey(Address, related_name='customer', on_delete=models.SET_DEFAULT, default='')

    def __str__(self):
        return f"{self.firstname}  {self.lastname}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, related_name='orders', on_delete=models.CASCADE)
    start_date = models.DateField('Дата заказа', db_index=True)
    start_time = models.TimeField('Время заказа', db_index=True)
    end_date = models.DateField('Дата завершения заказа', null=True, db_index=True)
    end_time = models.TimeField('Время завершения заказа', null=True, db_index=True)

    def __str__(self):
        return f'{self.id} {self.address} {self.start_date} {self.start_time} {self.end_date} {self.end_time}'


class Cart(models.Model):
    product = models.ForeignKey(Product, related_name='carts', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('количество')
    order = models.ForeignKey(Order, related_name='cart', on_delete=models.CASCADE)

    objects = CartQuerySet.as_manager()

    def __str__(self):
        return f'{self.order.id} {self.product} {self.quantity}'
