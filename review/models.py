from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import OrderItem

User = get_user_model()

class Review(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_index=True
    )
    text = models.TextField(verbose_name='متن نظر')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز',
        db_index=True
    )
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_user_product_review'
            )
        ]
        indexes = [
            models.Index(fields=['product', 'is_approved', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        display = getattr(self.user, 'get_full_name', lambda: '')() or getattr(self.user, 'phone', '') or getattr(self.user, 'email', '')
        return f'نظر {display} برای {getattr(self.product, "name", self.product_id)}'

    def get_absolute_url(self):
        return reverse('products:product-detail', kwargs={'pk': self.product_id})

    @property
    def is_verified_buyer(self):
        """Check if the user has purchased the product from the shop before"""
        try:
            from orders.models import OrderItem, Order
        except ImportError:
            return False
        if not self.user or not self.product:
            return False
        return OrderItem.objects.filter(
            order__customer=self.user,
            product_id=self.product.id,
            order__status__in=Order.Status.DELIVERED
        ).exists()
