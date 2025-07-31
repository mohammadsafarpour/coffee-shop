from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    template_name = 'products/product_create.html'
    fields = '__all__' #['category', 'name', 'slug', 'image', 'description', 'price', 'ingredients']
    success_url = reverse_lazy('product-list')