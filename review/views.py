from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from orders.models import OrderItem


def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.filter(is_approved=True)
    form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'purchased': OrderItem.objects.filter(order__customer=request.user, product=product).exists(),
        'form': form,
    }
    
    return render(request, 'review/product_reviews.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST':
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            
            # if Review.objects.filter(product=product, user=request.user).exists():
            #     messages.error(request, 'You have already reviewed this product.')
                # return redirect('review:product_reviews', product_id=product.id)

            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            try:
                review.save()
                messages.success(request, 'نظر شما با موفقیت ثبت شد و پس از تایید مدیر نمایش داده خواهد شد.')
                # return redirect('products:product-detail', pk=product.id)

            except IntegrityError:
                messages.error(request, 'شما قبلاً برای این محصول نظر داده‌اید.')
                # return redirect('products:product-detail', pk=product.id)
        # else:
        #     messages.error(request, 'لطفا فرم را به درستی پر کنید.')

        #     return redirect('review:product_reviews', product_id=product.id)
    else:
        form = ReviewForm()

    # reviews = product.reviews.filter(is_approved=True)
    # return render(request, 'review/product_reviews.html', {'form': form, 'product': product, 'reviews': product.reviews.filter(is_approved=True)})
    return redirect ('products:product-detail', pk=product.id)


# class UserReviewView(LoginRequiredMixin, generic.View):
#     def get(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         reviews = product.reviews.filter(is_approved=True)
#         form = ReviewForm()
#         return render(request, 'review/product_reviews.html', {'form': form, 'product': product, 'reviews': reviews})

#     def post(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = product
#             review.user = request.user
#             review.save()
#             return redirect('product-detail', pk=product.id)
#         return render(request, 'review/product_reviews.html', {'form': form, 'product': product, 'reviews': product.reviews.filter(is_approved=True)})


#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = product
#             review.user = request.user
#             review.save()
#             return redirect('product-detail', pk=product.id)
#     else:
#         form = ReviewForm()
    
#     return render(request, 'review/add_review.html', {'form': form, 'product': product})

# def review_index(request):
#     reviews = Review.objects.all()
#     return render(request, 'review/index.html', {'reviews': reviews})