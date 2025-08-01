from django.contrib import admin
from .models import OrderItem, Order

class OrderAdminInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
<<<<<<< Updated upstream
    list_display = ['id', 'customer', 'created_at', 'status', 'total_price']
=======
    list_display = ['id', 'customer', 'created_at', 'status', 'display_total_price']
>>>>>>> Stashed changes
    list_filter = ['customer', 'created_at', 'status']
    search_fields = ['id', 'customer__username']
    inlines = [OrderAdminInline]
    readonly_fields = ['created_at', 'updated_at']
    
    def display_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    display_total_price.short_description = 'Total Price'