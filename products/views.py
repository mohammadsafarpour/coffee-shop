from django.shortcuts import render, get_object_or_404

from django.views.generic import ListView, CreateView, DetailView
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

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'