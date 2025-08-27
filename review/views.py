from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import OuterRef, Exists
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from products.models import Product
from notification.models import Notification
from orders.models import Order, OrderItem
from .models import Review
from .forms import ReviewForm


def _user_purchased_product(user, product):
    if not user.is_authenticated:
        return False
    # try:
    #     from orders.models import OrderItem
    # except Exception:
    #     return False
    return OrderItem.objects.filter(order__customer=user, product=product).exists()

def product_reviews(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)

    delivered = getattr(getattr(Order, 'Status', None), 'DELIVERED', None)
    if delivered is None:
        status_list = None
    elif isinstance(delivered, (list, tuple, set)):
        status_list = list(delivered)
    else:
        status_list = [delivered]

    order_filter = {
        'order__customer': OuterRef('user'),
        'product': product,
    }
    if status_list:
        order_filter['order__status__in'] = status_list

    reviews_qs = (
        product.reviews.filter(is_approved=True)
        .select_related('user', 'user__profile')
        .annotate(verified_buyer=Exists(OrderItem.objects.filter(**order_filter)))
        .order_by('-created_at')
    )

    paginator = Paginator(reviews_qs, 200)
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    form = ReviewForm()
    purchased = request.user.is_authenticated and OrderItem.objects.filter(
        order__customer=request.user, product=product
    ).exists()

    return render(request, 'review/product_reviews.html', {
        'product': product,
        'reviews': reviews,
        'purchased': purchased,
        'form': form,
    })

def _create_admin_notifications(review):

    from django.contrib.auth import get_user_model
    User = get_user_model()
    managers = User.objects.filter(is_staff=True)
    for u in managers:
        Notification.objects.create(
            user=u,
            title='نظر جدید ثبت شد',
            message=f'نظر جدید برای "{review.product.name}" توسط {review.user} ثبت شد.',
            notification_type='review',
            content_object=review, 
        )
    return

@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    existing = Review.objects.filter(product=product, user=request.user).first()

    form = ReviewForm(request.POST, instance=existing)
    if not form.is_valid():
        for err in form.errors.values():
            messages.error(request, err)
        return redirect('products:product-detail', pk=product.id)

    review = form.save(commit=False)
    review.product = product
    review.user = request.user

    review.save()

    _create_admin_notifications(review)

    if review.is_approved:
        messages.success(request, 'نظر شما ثبت و نمایش داده شد.')
    else:
        messages.success(request, 'نظر شما ثبت شد و پس از تأیید مدیر نمایش داده می‌شود.')

    
    # return redirect('review:user_reviews')

    return redirect('products:product-detail', pk=product.id)

class UserReviewsView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'review/user_reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return (Review.objects
                .filter(user=self.request.user)
                .select_related('product', 'user')
                .order_by('-created_at'))
