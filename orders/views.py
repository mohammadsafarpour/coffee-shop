import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from products.models import Product, Category
from datetime import datetime, timedelta
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        try:
            quantity_to_add = int(request.POST.get('quantity', '1'))
            if quantity_to_add < 1:
                quantity_to_add = 1
        except (ValueError, TypeError):
            quantity_to_add = 1
    else:
        quantity_to_add = 1
    
    pid_str = str(product_id)
    current_quantity_in_cart = cart.get(pid_str, {}).get('quantity', 0)
    
    if (current_quantity_in_cart + quantity_to_add) > product.stock:
        messages.error(request, f'موجودی محصول "{product.name}" کافی نیست.')
        return redirect(request.META.get('HTTP_REFERER', 'product-list'))

    if pid_str in cart:
        cart[pid_str]['quantity'] += quantity_to_add
    else:
        cart[pid_str] = {'quantity': quantity_to_add, 'price': str(product.price)}
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f'{quantity_to_add} عدد "{product.name}" به سبد خرید اضافه شد.')
    return redirect('orders:cart_detail')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        request.session.modified = True
    return redirect('orders:cart_detail')

def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid_str = str(product_id)
    
    if pid_str in cart:
        product = get_object_or_404(Product, id=int(pid_str))
        
        if cart[pid_str]['quantity'] < product.stock:
            cart[pid_str]['quantity'] += 1
            request.session.modified = True
        else:
            messages.warning(request, f'حداکثر موجودی برای محصول "{product.name}" در سبد شما قرار دارد.')
        
    return redirect('orders:cart_detail')

def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        if cart[pid_str]['quantity'] > 1:
            cart[pid_str]['quantity'] -= 1
        else:
            del cart[pid_str]
        request.session.modified = True
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart_session = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for pid, item_data in cart_session.items():
        product = get_object_or_404(Product, id=int(pid))
        item_total = product.price * item_data['quantity']
        cart_items.append({'product': product, 'quantity': item_data['quantity'], 'total_price': item_total})
        total_price += item_total
    
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'orders/cart_detail.html', context)


if getattr(settings, 'SANDBOX', False):
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/{{authority}}"

@login_required
def payment_request(request):
    cart_session = request.session.get('cart', {})
    if not cart_session:
        return redirect('orders:cart_detail')

    for pid, item_data in cart_session.items():
        product = get_object_or_404(Product, id=int(pid))
        if item_data['quantity'] > product.stock:
            messages.error(request, f'موجودی محصول "{product.name}" کافی نیست. لطفاً سبد خرید خود را ویرایش کنید.')
            return redirect('orders:cart_detail')

    total_price = sum(int(item_data['price']) * item_data['quantity'] for item_data in cart_session.values())
    amount_in_rials = total_price * 10
    
    merchant_id = getattr(settings, 'MERCHANT_ID', 'YOUR_MERCHANT_ID')

    request_data = {
        "merchant_id": merchant_id,
        "amount": amount_in_rials,
        "callback_url": request.build_absolute_uri(reverse('orders:payment_verify')),
        "description": "خرید از کافه تمیز",
        "metadata": {"mobile": request.user.phone, "email": request.user.email}
    }
    
    request_header = {"accept": "application/json", "content-type": "application/json"}
    try:
        res = requests.post(ZP_API_REQUEST, data=json.dumps(request_data), headers=request_header, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 'data' in data and data['data'] and data['data']['code'] == 100:
            authority = data['data']['authority']
            return redirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            error_message = data.get('errors', {'message': 'پاسخ نامعتبر از درگاه پرداخت.'})
            return render(request, 'orders/payment_error.html', {'error': error_message})
    except requests.exceptions.RequestException as e:
        return render(request, 'orders/payment_error.html', {'error': f'خطا در ارتباط با سرور پرداخت: {e}'})

@login_required
def payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    if not authority or status != 'OK':
        return render(request, 'orders/payment_error.html', {'error': 'پرداخت با خطا مواجه شد یا توسط کاربر لغو شد.'})

    cart_session = request.session.get('cart', {})
    if not cart_session:
        return render(request, 'orders/payment_error.html', {'error': 'سبد خرید شما منقضی شده است.'})
    
    total_price = sum(int(item_data['price']) * item_data['quantity'] for item_data in cart_session.values())
    amount_in_rials = total_price * 10
    
    merchant_id = getattr(settings, 'MERCHANT_ID', 'YOUR_MERCHANT_ID')

    verify_data = {
        "merchant_id": merchant_id,
        "amount": amount_in_rials,
        "authority": authority,
    }
    request_header = {"accept": "application/json", "content-type": "application/json"}
    try:
        res = requests.post(ZP_API_VERIFY, data=json.dumps(verify_data), headers=request_header, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 'data' in data and data['data'] and data['data']['code'] in [100, 101]:
            order = Order.objects.create(
                customer=request.user,
                is_paid=True,
                status=Order.Status.PENDING
            )
            for product_id, item_data in cart_session.items():
                product = Product.objects.get(id=int(product_id))
                
                if product.stock < item_data['quantity']:
                    messages.error(request, f"متاسفانه در حین پرداخت، موجودی محصول {product.name} به اتمام رسید.")
                    order.delete()
                    return redirect('orders:cart_detail')

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=product.price
                )
                product.stock -= item_data['quantity']
                product.save()
            
            del request.session['cart']
            request.session.modified = True
            
            ref_id = data['data'].get('ref_id', '')
            messages.success(request, f'سفارش شما با موفقیت ثبت شد. شماره پیگیری: {ref_id}')
            return render(request, 'orders/payment_success.html', {'ref_id': ref_id, 'order': order})
        else:
            error_message = data.get('errors', {'message': 'تراکنش ناموفق بود یا قبلا تایید شده است.'})
            return render(request, 'orders/payment_error.html', {'error': error_message})
    except requests.exceptions.RequestException as e:
        return render(request, 'orders/payment_error.html', {'error': f'خطا در تایید پرداخت: {e}'})

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('order_items__product__category')
    
    time_filter = request.GET.get('time_filter')
    category_filter = request.GET.get('category')

    if time_filter == 'week':
        orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=7))
    elif time_filter == 'month':
        orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=30))

    if category_filter:
        orders = orders.filter(order_items__product__category__id=category_filter).distinct()
    
    context = {
        'orders': orders,
        'categories': Category.objects.all(),
        'current_time_filter': time_filter,
        'current_category_filter': int(category_filter) if category_filter else None,
    }
    return render(request, 'orders/order_list.html', context)

class OrderHistoryApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)