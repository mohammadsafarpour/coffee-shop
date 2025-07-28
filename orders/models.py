from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.models import CustomUser
from products.models import Product



class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(choices=[('pending', 'Pending'), ('delivered', 'Delivered')], default='Delivered')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()