from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Order, OrderItem
from products.models import Product
from .serializers import OrderSerializer

class OrderHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('order_items__product')

    def create(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        if not cart_session:
            return Response(
                {'error': 'سبد خرید شما خالی است.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        for pid, item_data in cart_session.items():
            product = get_object_or_404(Product, id=int(pid))
            if item_data['quantity'] > product.stock:
                return Response(
                    {'error': f'موجودی محصول "{product.name}" کافی نیست.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(customer=request.user, is_paid=True)
        
        for product_id, item_data in cart_session.items():
            product = Product.objects.get(id=int(product_id))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
            product.stock -= item_data['quantity']
            product.save()

        del request.session['cart']
        request.session.modified = True
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def kitchen_queue(self, request):

        pending_orders = Order.objects.filter(is_paid=True, status=Order.Status.PENDING).order_by('created_at')
        
        page = self.paginate_queryset(pending_orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)