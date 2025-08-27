# from django.contrib import admin
# from .models import Product, Category, Ingredient, ProductImage, Favorite

# admin.site.register(Product)
# admin.site.register(Category)
# admin.site.register(Ingredient)
# admin.site.register(ProductImage)
# admin.site.register(Favorite)

# products/admin.py

#-----------------------------------
# ----------------------------------

from django.contrib import admin
from .models import Product, Category, Ingredient, ProductImage #, Favorite
from django.utils.html import format_html

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1

# class FavoriteInline(admin.TabularInline):
#     model = Favorite
#     extra = 0
#     readonly_fields = ('product',)
#     can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image_preview', 'stock', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, IngredientInline]
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "پیش‌نمایش"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    search_fields = ('name',)
    autocomplete_fields = ['product']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview')
    search_fields = ('product__name',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "پیش‌نمایش"

# @admin.register(Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'created_at')
#     readonly_fields = ('created_at',)
