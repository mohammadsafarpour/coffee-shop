from django.db import models
from accounts.models import CustomUser
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
# from django.conf import settings

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name="متن نظر")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز"
    )
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده") 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # unique_together = ('product', 'user')

    def __str__(self):
        user_display_name = self.user.get_full_name() or self.user.phone
        return f'نظر {user_display_name} برای {self.product.name}'


# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     text = models.TextField()
#     rating = models.PositiveIntegerField(default=5)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Review by {self.user.username} on {self.product.name}"