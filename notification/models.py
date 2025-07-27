from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.models import CustomUser


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return self.name

    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comments = models.TextField(null=True, blank=True)


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(choices=[('pending', 'Pending'), ('delivered', 'Delivered')], default='Delivered')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()


class Favorite(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Rating(models.Model):
    rate = [(1, 'very bad'), (2, "bad"), (3, "normal"), (4, "good"), (5, "very good")]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Rating_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='Rating_product')
    score = models.CharField(choices=rate)


class Ingredient(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title