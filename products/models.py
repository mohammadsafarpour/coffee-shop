from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='products/', null=True, blank=True)

    api_tags = models.JSONField(default=list, blank=True)
    api_main_image = models.ForeignKey(
        "ProductImage", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="main_for"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.product.name})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
        
    class Meta:
        ordering = ['id']
        verbose_name = "Product Image"