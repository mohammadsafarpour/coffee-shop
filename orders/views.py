import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    try:
        quantity = int(request.GET.get('quantity', '1'))
        if quantity < 1: quantity = 1
    except (ValueError, TypeError):
        quantity = 1
        
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity, 'price': str(product.price)}

    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect(request.META.get('HTTP_REFERER', 'product-list'))

def cart_detail(request):
    cart_session = request.session.get('cart', {})
    cart_items_for_template = []
    total_cart_price = 0

    for product_id, item_data in cart_session.items():
        product = get_object_or_404(Product, id=int(product_id))
        total_item_price = product.price * item_data['quantity']
        
        cart_items_for_template.append({
            'product': product,
            'quantity': item_data['quantity'],
            'total_price': total_item_price
        })
        total_cart_price += total_item_price

    context = {
        'cart_items': cart_items_for_template,
        'total_price': total_cart_price,
    }
    return render(request, 'orders/cart_detail.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('orders:cart_detail')

def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('orders:cart_detail')

def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        if cart[product_id_str]['quantity'] > 1:
            cart[product_id_str]['quantity'] -= 1
        else:
            del cart[product_id_str]
        
        request.session['cart'] = cart
        request.session.modified = True
            
    return redirect('orders:cart_detail')


if settings.SANDBOX:
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

    total_price = sum(int(item_data['price']) * item_data['quantity'] for item_data in cart_session.values())
    amount_in_rials = total_price * 10

    request_data = {
        "merchant_id": settings.MERCHANT_ID,
        "amount": amount_in_rials,
        "callback_url": request.build_absolute_uri(reverse('orders:payment_verify')),
        "description": "خرید از کافه تمیز",
        "metadata": {"mobile": request.user.phone, "email": request.user.email}
    }
    
    request_header = {"accept": "application/json", "content-type": "application/json"}
    res = requests.post(ZP_API_REQUEST, data=json.dumps(request_data), headers=request_header)
    data = res.json()
    
    if res.status_code == 200 and 'data' in data and data['data'] and data['data']['code'] == 100:
        authority = data['data']['authority']
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        error_message = data.get('errors', 'خطایی در ارتباط با درگاه پرداخت رخ داد.')
        return render(request, 'orders/payment_error.html', {'error': error_message})

def payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    if not authority or status != 'OK':
        return render(request, 'orders/payment_error.html', {'error': 'پرداخت با خطا مواجه شد یا توسط کاربر لغو شد.'})

    cart_session = request.session.get('cart', {})
    total_price = sum(int(item_data['price']) * item_data['quantity'] for item_data in cart_session.values())
    amount_in_rials = total_price * 10
    
    verify_data = {
        "merchant_id": settings.MERCHANT_ID,
        "amount": amount_in_rials,
        "authority": authority,
    }
    request_header = {"accept": "application/json", "content-type": "application/json"}
    res = requests.post(ZP_API_VERIFY, data=json.dumps(verify_data), headers=request_header)
    data = res.json()

    if res.status_code == 200 and 'data' in data and data['data'] and data['data']['code'] in [100, 101]:
        order = Order.objects.create(
            customer=request.user,
            is_paid=True,
            status=Order.Status.PENDING
        )
        for product_id, item_data in cart_session.items():
            product = Product.objects.get(id=int(product_id))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
        
        del request.session['cart']
        request.session.modified = True
        
        ref_id = data['data'].get('ref_id', '')
        return render(request, 'orders/payment_success.html', {'ref_id': ref_id})
    else:
        error_message = data.get('errors', 'تراکنش ناموفق بود یا قبلا تایید شده است.')
        return render(request, 'orders/payment_error.html', {'error': error_message})



@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'orders/list.html', {'orders': orders})