from rest_framework import serializers
from products.models import Product, Category
from .models import Order, OrderItem

class SimpleProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category_name']
        
class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
    
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'order_items']

