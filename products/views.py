from typing import Optional
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Exists, OuterRef
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from review.forms import ReviewForm
from .models import Product
from orders.models import OrderItem
from notification.models import Notification


# -----------------------
# Class-based Views
# -----------------------

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 8


class ProductCreateView(CreateView):
    model = Product
    template_name = 'products/product_create.html'
    fields = ['category', 'name', 'slug', 'image', 'description', 'price', 'is_active', 'stock']
    success_url = reverse_lazy('products:product-list')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_reviews_qs(self, product):
        return (
            product.reviews.filter(is_approved=True)
            .select_related('user', 'user__profile')
            .annotate(
                is_verified_buyer=Exists(
                    OrderItem.objects.filter(
                        order__customer=OuterRef('user'),
                        product=product
                    )
                )
            )
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        user = self.request.user
        is_auth = user.is_authenticated

        reviews_qs = self.get_reviews_qs(product)
        reviews_with_status = [
            {
                'review': r,
                'is_owner': is_auth and r.user_id == user.id,
                'is_verified_buyer': bool(getattr(r, 'is_verified_buyer', False)),
            }
            for r in reviews_qs
        ]

        avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] or 0
        context.update({
            'reviews_with_status': reviews_with_status,
            'reviews_count': reviews_qs.count(),
            'average_rating': int(round(avg_rating)) if avg_rating else 0,
            'is_favorite': is_auth and user.profile.favorites.filter(pk=product.pk).exists(),
            'has_purchased': is_auth and OrderItem.objects.filter(order__customer=user, product=product).exists(),
            'has_reviewed': is_auth and product.reviews.filter(user=user).exists(),
            'review_form': ReviewForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            messages.error(request, 'برای ارسال نظر وارد شوید.')
            return redirect(f"/accounts/login/?next={request.path}")

        form = ReviewForm(request.POST, request.FILES or None)
        if not form.is_valid():
            context = self.get_context_data()
            context['review_form'] = form
            messages.error(request, 'ارسال ناموفق. فرم را دقیق پر کنید.')
            return render(request, self.template_name, context)

        review = self.object.reviews.filter(user=request.user).first()
        data = form.cleaned_data
        if review:
            review.rating = data.get('rating')
            review.text = data.get('text')
            review.is_approved = False
            review.save()
            messages.success(request, 'نظر شما بروزرسانی شد و برای تأیید ارسال شد.')
        else:
            self.object.reviews.create(
                user=request.user,
                rating=data.get('rating'),
                text=data.get('text'),
                is_approved=False
            )
            messages.success(request, 'نظر شما ثبت شد و برای تأیید ارسال شد.')

        return redirect(self.object.get_absolute_url() if hasattr(self.object, 'get_absolute_url') else request.path)


class ProductCategoryView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs.get('category_slug'))


# -----------------------
# Function-based Views
# -----------------------

@login_required
def add_to_favorites(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    profile.favorites.add(product)

    try:
        Notification.objects.create(
            user=request.user,
            title='افزوده شد به علاقه‌مندی‌ها',
            message=f'{product.name} به علاقه‌مندی‌های شما اضافه شد',
            target_url=reverse_lazy('products:product-detail', args=[product.pk]),
        )
    except Exception:
        pass

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_favorites(request, product_id: int) -> Optional[redirect]:
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    profile.favorites.remove(product)

    try:
        Notification.objects.create(
            user=request.user,
            title='حذف از علاقه‌مندی‌ها',
            message=f'محصول {product.name} از علاقه‌مندی‌ها حذف شد',
            target_url=reverse_lazy('products:product-detail', args=[product.pk]),
        )
    except Exception:
        pass

    return redirect(request.META.get('HTTP_REFERER', '/'))


def product_reviews(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    reviews_list = product.reviews.filter(is_approved=True).order_by('-created_at')
    form = ReviewForm()

    paginator = Paginator(reviews_list, 200)
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    purchased = False
    if request.user.is_authenticated:
        purchased = OrderItem.objects.filter(order__customer=request.user, product=product).exists()

    context = {
        'product': product,
        'reviews': reviews,
        'purchased': purchased,
        'form': form,
    }
    return render(request, 'review/product_reviews.html', context)
