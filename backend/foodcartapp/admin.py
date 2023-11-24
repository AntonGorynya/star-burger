from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem, Customer, Address, OrderedProduct, Order


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ['position_sum']
    extra = 0

    @admin.display(description="Сумма позиции")
    def position_sum(self, obj):
        print(obj) # если убрать, то не работает
        return obj.quantity * obj.fixed_price


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['start_date']
    inlines = [
        OrderedProductInline,
    ]
    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        try:
            if 'next' in request.GET:
                URLValidator(request.GET['next'])
                return HttpResponseRedirect(request.GET['next'])
        except ValidationError:
            return response
        finally:
            return response
