# review/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.auth.decorators import login_required

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product-detail', pk=product.id)
    else:
        form = ReviewForm()
    
    return render(request, 'review/add_review.html', {'form': form, 'product': product})

def review_index(request):
    reviews = Review.objects.all()
    return render(request, 'review/index.html', {'reviews': reviews})