from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Avg
from review.forms import ReviewForm
from .models import Product
from orders.models import OrderItem


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

# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, 'products/product_detail.html', {'product': product})

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
            has_purchased = OrderItem.objects.filter(
                order__customer=user,
                product=product
            ).exists()
            context['has_purchased'] = has_purchased
        else:
            context['is_favorite'] = False

        reviews = product.reviews.filter(is_approved=True)
        context['reviews'] = reviews
        context['reviews_count'] = reviews.count()

        average = reviews.aggregate(Avg('rating')).get('rating__avg')
        context['average_rating'] = round(average) if average else 0
        
        reviews_with_status = []
        for review in reviews:
            reviews_with_status.append({
                'review': review,
                'is_owner': review.user == user
            })
        context['review_form'] = ReviewForm()

        # context['reviews'] = reviews_with_status

        # has_purchased = OrderItem.objects.filter(order__customer=review.user, product=product).exists()

        # reviews_with_status.append({'review': review, 'has_purchased': has_purchased})
        
        # context['reviews_with_status'] = reviews_with_status

            
        return context
    

@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.user.profile.favorites.add(product)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    profile.favorites.remove(product)
    return redirect(request.META.get('HTTP_REFERER'))

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