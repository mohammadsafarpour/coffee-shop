from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from accounts.models import Profile
from .models import Product #, Favorite



class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    template_name = 'products/product_create.html'
    fields = '__all__' #['category', 'name', 'slug', 'image', 'description', 'price', 'ingredients']
    # exclude = ['']
    
    success_url = reverse_lazy('products:product-list')

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            context['is_favorite'] = self.request.user.profile.favorites.filter(pk=product.pk).exists()
        else:
            context['is_favorite'] = False
        return context

@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.user.profile.favorites.add(product)
    return redirect(request.META.get('HTTP_REFERER'), 'product-detail')

@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    profile.favorites.remove(product)
    return redirect(request.META.get('HTTP_REFERER'), 'product-detail')

class ProductCategoryView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Product.objects.filter(category__slug=category_slug)


# @login_required
# def toggle_favorite(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     profile = request.user.profile
#     favorite = profile.favorites.filter(product=product).first()


#     if favorite:
#         profile.favorites.remove(product)
#     else:
#         profile.favorites.add(product)

    
#     return redirect('product-detail', pk=product_id)