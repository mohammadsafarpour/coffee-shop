from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem

# @login_required
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/list.html', {'orders': orders})
    