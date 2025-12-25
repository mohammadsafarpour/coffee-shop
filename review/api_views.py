from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q, Exists, OuterRef
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Review
from .permissions import IsReviewOwnerOrAdminOrReadOnly
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewListSerializer,
    ReviewStatsSerializer,
    ProductReviewStatsSerializer
)
from products.models import Product
from orders.models import OrderItem, Order
from notification.models import Notification


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'is_approved', 'product']
    search_fields = ['text', 'user__phone', 'product__name']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'product')
        
        if self.request.user.is_staff:
            return queryset.all()
        
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_approved=True) | Q(user=self.request.user)
            )
        
        return queryset.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer

    @extend_schema(
        responses={
            200: ReviewStatsSerializer,
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        queryset = Review.objects.all()
        
        total_reviews = queryset.count()
        approved_reviews = queryset.filter(is_approved=True).count()
        pending_reviews = total_reviews - approved_reviews
        average_rating = queryset.aggregate(avg=Avg('rating'))['avg'] or 0
        
        rating_dist = {}
        for i in range(1, 6):
            rating_dist[str(i)] = queryset.filter(rating=i).count()
        
        data = {
            'total_reviews': total_reviews,
            'approved_reviews': approved_reviews,
            'pending_reviews': pending_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_dist
        }
        
        serializer = ReviewStatsSerializer(data)
        return Response(serializer.data)
    
    @extend_schema(
        responses={
            200: ReviewListSerializer(many=True),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        queryset = Review.objects.filter(is_approved=False).order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="نظر تأیید شد"),
            404: OpenApiResponse(description="نظر یافت نشد")
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        
        try:
            Notification.objects.create(
                user=review.user,
                title='نظر شما تأیید شد',
                message=f'نظر شما برای محصول "{review.product.name}" تأیید و منتشر شد.',
                notification_type='review',
                content_object=review
            )
        except Exception:
            pass
        
        return Response({'message': 'نظر تأیید شد'})

    @extend_schema(
        responses={
            200: OpenApiResponse(description="نظر رد شد"),
            404: OpenApiResponse(description="نظر یافت نشد")
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.is_approved = False
        review.save(update_fields=['is_approved'])
        
        try:
            Notification.objects.create(
                user=review.user,
                title='نظر شما رد شد',
                message=f'نظر شما برای محصول "{review.product.name}" رد شد.',
                notification_type='review',
                content_object=review
            )
        except Exception:
            pass
        
        return Response({'message': 'نظر رد شد'})

    @extend_schema(
        responses={
            200: ReviewListSerializer(many=True),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        queryset = Review.objects.filter(user=request.user).order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewListSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()
        
        # try:
        #     from django.contrib.auth import get_user_model
        #     User = get_user_model()
        #     managers = User.objects.filter(is_staff=True)
            
        #     for admin in managers:
        #         Notification.objects.create(
        #             user=admin,
        #             title='نظر جدید ثبت شد',
        #             message=f'نظر جدید برای محصول "{review.product.name}" توسط {review.user} ثبت شد.',
        #             notification_type='review',
        #             content_object=review
        #         )
        # except Exception:
        #     pass
        
@extend_schema(
    methods=['get'],
    responses={200: ProductReviewStatsSerializer}
)
@extend_schema(
    methods=['post'],
    request=ReviewCreateSerializer,
    responses={
        201: ReviewSerializer,
        400: OpenApiResponse(description="خطاهای اعتبارسنجی")
    }
)
class ProductReviewViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk')
        
        delivered_statuses = getattr(Order.Status, 'DELIVERED', [])
        if not isinstance(delivered_statuses, (list, tuple)):
            delivered_statuses = [delivered_statuses]
        
        queryset = Review.objects.filter(product_id=product_pk).select_related(
            'user', 'product'
        ).annotate(
            verified_buyer=Exists(
                OrderItem.objects.filter(
                    order__customer=OuterRef('user'),
                    product_id=product_pk,
                    order__status__in=delivered_statuses
                )
            )
        )
        
        if self.request.user.is_staff:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_approved=True) | Q(user=self.request.user)
            )
        else:
            return queryset.filter(is_approved=True)

    @action(detail=False, methods=['get'])
    def stats(self, request, product_pk=None):
        product = get_object_or_404(Product, pk=product_pk)
        queryset = Review.objects.filter(product=product, is_approved=True)
        
        total_reviews = queryset.count()
        average_rating = queryset.aggregate(avg=Avg('rating'))['avg'] or 0
        
        rating_dist = {}
        for i in range(1, 6):
            rating_dist[str(i)] = queryset.filter(rating=i).count()
        
        data = {
            'product_id': product.id,
            'product_name': product.name,
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_dist
        }
        
        serializer = ProductReviewStatsSerializer(data)
        return Response(serializer.data)