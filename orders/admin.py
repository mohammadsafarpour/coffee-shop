from django.contrib import admin
from .models import OrderItem, Order

class OrderAdminInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'status']
    list_filter = ['customer', 'created_at', 'status']
    search_fields = ['created_at']
    # search_fields = ['customer__username']
    inlines = [OrderAdminInline]
    readonly_fields = ['created_at', 'updated_at']