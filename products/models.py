# from django.db import models
# from django.conf import settings
# from django.urls import reverse

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100, unique=True)

#     class Meta:
#         ordering = ('name',)
#         indexes = [
#             models.Index(fields=['name']),
#         ]
#         verbose_name_plural = 'Categories'
#         verbose_name = 'Category'

#     def __str__(self):
#         return self.name
    
#     def get_absolute_url(self):
#         return reverse('products:category_detail', args=[self.slug])


# class Ingredient(models.Model):
#     product = models.ForeignKey(
#         'Product',
#         on_delete=models.CASCADE,
#         related_name='ingredients'
#     )
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     name = models.CharField(max_length=200)
#     slug = models.SlugField(max_length=200, unique=True)
#     image = models.ImageField(upload_to='products/%Y/%m/%d', null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     available = models.BooleanField(default=True)
#     created = models.DateTimeField(auto_now_add=True)
#     main_ingredient = models.ManyToManyField(Ingredient, related_name='products')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     comments = models.TextField(null=True, blank=True)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     stock = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)

#     def get_absolute_url(self):
#         return reverse('products:product_detail', args=[self.id, self.slug])

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ('name',)
#         indexes = [
#             models.Index(fields=['name']),
#             models.Index(fields=['id', 'slug']),
#             models.Index(fields=['-created']),
#         ]
#         verbose_name_plural = 'Products'
#         verbose_name = 'Product'

# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='product_images/')
#     order = models.PositiveIntegerField(default=0)
    
#     class Meta:
#         ordering = ['order']

# class Favorite(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     created = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'product')

# products/models.py

from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)



    def __str__(self):
        return self.name

class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.product.name})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} {self.product}"
