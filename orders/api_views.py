from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from products.models import Product
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    CartSyncSerializer,
    OrderStatusUpdateSerializer,
)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_cart(self, user):
        cart, created = Order.objects.get_or_create(customer=user, is_paid=False)
        return cart

    @action(detail=False, methods=['get'], url_path='view')
    def view_cart(self, request):
        cart = self.get_cart(request.user)
        serializer = OrderSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        request=CartSyncSerializer,
        responses={200: OrderSerializer}
    )
    @action(detail=False, methods=['post'], url_path='sync')
    def sync_cart(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items_data = serializer.validated_data['items']

        with transaction.atomic():
            cart.order_items.all().delete()
            
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                if product.stock < quantity:
                    raise ValidationError(f'موجودی محصول "{product.name}" کافی نیست.')

                OrderItem.objects.create(
                    order=cart,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
        
        cart_serializer = OrderSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        cart = self.get_cart(request.user)
        if not cart.order_items.exists():
            return Response({'error': 'سبد خرید خالی است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            for item in cart.order_items.all():
                product = Product.objects.select_for_update().get(id=item.product.id)
                if product.stock < item.quantity:
                    raise ValidationError(f'موجودی محصول "{product.name}" کافی نیست.')
                product.stock -= item.quantity
                product.save()
            
            cart.is_paid = True
            cart.status = Order.Status.PENDING
            cart.save()
            
        return Response(OrderSerializer(cart).data)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.filter(is_paid=True).prefetch_related('order_items__product', 'customer__profile')
        return Order.objects.filter(customer=user, is_paid=True).prefetch_related('order_items__product')

    @extend_schema(
        request=OrderStatusUpdateSerializer,
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def manage_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='kitchen-queue')
    def kitchen_queue(self, request):
        pending_orders = Order.objects.filter(is_paid=True, status=Order.Status.PENDING).order_by('created_at')
        
        page = self.paginate_queryset(pending_orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)