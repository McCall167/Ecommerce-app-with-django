from gc import get_objects
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Cart, Order, OrderItem
import stripe


def signup_view(request):
    if request.method == 'POST': 
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else: 
            form = UserCreationForm()
        return render(request, 'signup.html', {'form': form}) 
    

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else :
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form})
        

def logout_view(request):
    if request.method == 'POST': 
        logout(request)
        return redirect('home')     


def product_list(request):
    products = Product.objects.all
    return render(request, 'product_list.html', {'products':products})

def product_detail(request, pk):
    product = get_object_or_404(product, pk=pk)
    return render(request, 'product_detail.html', {'product':product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created= Cart.objects.get_or_create(user=request.user, product=Product)
    if not created:
            cart_item.quantity += 1
            cart_item.save()
    return redirect('cart_detail')

def cart_detail(request):
    cart_items = get_objects.filter(user=request.user)
    return render(request, 'cart_detail.html', {'cart_items':cart_items})

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(Cart, user=request.user, product=product)
    cart_item.delete()
    return redirect('cart_detail')

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total=cart_total(cart_items))
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            item.delete()
        return redirect('order_confirmation', order_id=order.id)
    return render(request, 'checkout.html', {'cart_items': cart_items})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})

def cart_total(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)


stripe.api_key = 'your_stripe_secret_key'

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        charge = stripe.Charge.create(
            amount=int(cart_total(cart_items) * 100),
            currency='usd',
            description='E-commerce Order',
            source=token,
        )
        order = Order.objects.create(user=request.user, total=cart_total(cart_items))
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            item.delete()
        return redirect('order_confirmation', order_id=order.id)
    return render(request, 'checkout.html', {'cart_items': cart_items})

