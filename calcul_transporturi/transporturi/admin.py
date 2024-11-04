from django.contrib import admin
from .models import Transport


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = (
    'destination',  'id', 'client','delivery_date', 'pickup_time', 'get_prices', 'is_departed', 'is_completed',)
    list_filter = ('is_departed', 'is_completed', 'delivery_date', 'destination')
    search_fields = ('client__username', 'destination')
    filter_horizontal = ('transporters',)

    def get_prices(self, obj):

        prices = obj.prices.all()
        return ', '.join(f'{price.transporter.username}: {price.price}' for price in prices)

    get_prices.short_description = 'Prețuri'

