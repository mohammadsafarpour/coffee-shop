from django.shortcuts import render, get_object_or_404, redirect
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


@login_required
def order_list(request):

    orders = Order.objects.filter(customer=request.user)
    return render(request, 'orders/list.html', {'orders': orders})