def cart_context(request):

    cart_session = request.session.get('cart', {})
    
    cart_items_count = sum(item['quantity'] for item in cart_session.values())

    return {
        'cart_session': cart_session,
        'cart_items_count': cart_items_count,
    }