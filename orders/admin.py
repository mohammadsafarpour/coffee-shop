from django.contrib import admin
from .models import OrderItem, Order

class OrderAdminInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'status', 'display_total_price']
    list_filter = ['customer', 'created_at', 'status']
    search_fields = ['id', 'customer__username']
    inlines = [OrderAdminInline]
    readonly_fields = ['created_at', 'updated_at']
    
    def display_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    display_total_price.short_description = 'Total Price'
    
    # def save_related(self, request, form, formsets, change):    <==  Instead of a signals.py
    #     super().save_related(request, form, formsets, change)
    #     for item in form.instance.order_items.all():
    #         if item.product and (item.price is None or item.price == 0):
    #             item.price = item.product.price * item.quantity
    #             item.save()
