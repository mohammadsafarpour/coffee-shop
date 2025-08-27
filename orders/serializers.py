from rest_framework import serializers
from products.serializers import ProductSerializer
from accounts.serializers import CustomUserSerializer
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'created_at', 'is_paid', 'status', 'status_display',
            'total_price', 'order_items'
        ]

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class CartItemSyncSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product'
    )
    quantity = serializers.IntegerField(min_value=1)

class CartSyncSerializer(serializers.Serializer):
    items = CartItemSyncSerializer(many=True)