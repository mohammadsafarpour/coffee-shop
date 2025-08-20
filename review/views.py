from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from orders.models import OrderItem
from notification.models import Notification


def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.filter(is_approved=True)
    form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "purchased": OrderItem.objects.filter(
            order__customer=request.user, product=product
        ).exists(),
        "form": form,
    }

    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, "شما قبلاً برای این محصول نظر داده‌اید.")
        return redirect("products:product-detail", pk=product.id)

    return render(request, "review/product_reviews.html", context)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == "POST":
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            if not review.is_approved:
                Notification.objects.create(
                    user=review.user,
                    text=f"نظر جدیدی برای محصول {product.name} ثبت شده است و پس از تایید مدیر نمایش داده خواهد شد.",
                    notification_type=review,
                )
            messages.success(
                request,
                "نظر شما با موفقیت ثبت شد و پس از تایید مدیر نمایش داده خواهد شد.",
            )
            return redirect("review:user_reviews")
    else:
        form = ReviewForm()

    return redirect("review:product_reviews", product_id=product.id)


class UserReviewsView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "review/user_reviews.html"
    context_object_name = "reviews"

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related(
            "product", "product__category"
        ).order_by("-created_at")


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
