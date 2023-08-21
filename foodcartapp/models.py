from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from django.utils.timezone import now, localtime, localdate
from phonenumber_field.modelfields import PhoneNumberField


class CartQuerySet(models.QuerySet):
    def get_price(self,  *args, **kwargs):
        #print(sum([item.quantity*item.product.price for item in self]))
        return self.aggregate(total=Sum(F('quantity')*F('fixed_price')))['total']


class OrderQuerySet(models.QuerySet):
    def get_actual_orders(self, *args, **kwargs):
        return self.filter(end_date=None).select_related('customer').select_related('address').order_by('restaurant')


class Address(models.Model):
    address = models.CharField('Адрес', max_length=50)
    lat = models.FloatField('Широта', null=True)
    lon = models.FloatField('Долгота', null=True)

    def __str__(self):
        return f'{self.address}'


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        related_name='restaurant',
        verbose_name='Адресс',
        on_delete=models.CASCADE
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


class Customer(models.Model):
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона')
    address = models.ForeignKey(Address, related_name='customer', on_delete=models.SET_DEFAULT, default='')

    def __str__(self):
        return f"{self.firstname}  {self.lastname}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, verbose_name='Клиент')
    address = models.ForeignKey(Address, related_name='orders', on_delete=models.CASCADE, verbose_name='Адрес')
    start_date = models.DateTimeField('Дата заказа', db_index=True, default=now)
    called_at = models.DateTimeField('Дата время звонка', db_index=True, blank=True, null=True)
    end_date = models.DateTimeField('Дата завершения заказа', null=True, blank=True, db_index=True)
    comments = models.TextField(null=True, blank=True, verbose_name='Комментарий к заказу', max_length=500, default='')
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Ответственный Ресторан',
        null=True
    )
    status = models.CharField(
        max_length=2,
        choices=[
            ('MR', 'Необработан'),
            ('RN', 'готовится'),
            ('DY', 'в доставке')
        ],
        default='MR',
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=1,
        choices=[
            ('C', 'Наличные'),
            ('E', 'Банковской картой')
        ],
        default='E',
        verbose_name='Способ оплаты',
        db_index=True
    )
    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.id} {self.address} {self.start_date} {self.end_date}'


class Cart(models.Model):
    product = models.ForeignKey(Product, related_name='carts', on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('количество')
    order = models.ForeignKey(Order, related_name='cart', on_delete=models.CASCADE)
    fixed_price = models.DecimalField(
        'цена за штуку',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def position_sum(self):
        if self.fixed_price:
            return self.quantity * self.fixed_price

    objects = CartQuerySet.as_manager()

    def __str__(self):
        return f'{self.order.id} {self.product} {self.quantity}'
