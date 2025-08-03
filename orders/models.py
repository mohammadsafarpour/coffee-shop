from django.db import models
from accounts.models import CustomUser
from products.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pe', 'Pending'
        DELIVERED = 'del', 'Delivered'
        
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            # models.Index(fields=['status']),
            # models.Index(fields=['customer']),
        ]
        
    def __str__(self):
        return f"Order #{self.id} - {self.customer.email}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.order_items.all()) 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product')

    @property
    def total_price(self):
        return self.quantity * self.price