from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json 
import datetime
from .utils import cartData, guestOrder

# Create your views here.

def about(request):
    context = {}
    return render(request, 'store/about.html', context)


def store(request):
    if 'query' in request.GET:
        query = request.GET['query']
        products = Product.objects.filter(name__icontains=query)
        data = cartData(request)
        cartItems = data['cartItems']
        context = {'products': products , 'cartItems':cartItems, 'query': query}
        return render(request, 'store/store.html' , context)

    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products': products , 'cartItems':cartItems}
    return render(request, 'store/store.html' , context)
        
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = { 'items': items, 'order':order, 'cartItems':cartItems} 
    return render(request, 'store/cart.html' , context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = { 'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html' , context)

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
           
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, 'Username OR password is incorrect')
        
    context = {}
    return render(request, 'store/loginpage.html', context)


def Register(request):
    if request.method == 'POST':
        username =request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            # Ensure a related Customer is created for the new User
            Customer.objects.get_or_create(user=user, defaults={'name': username, 'email': email})
            messages.success(request, 'Account was created for ' + username)
            return redirect('loginpage')
        except:
            messages.error(request, 'An error occurred during registration')
    context = {}
    return render(request, 'store/register.html', context)

def ProductImage(request, pk):
    product = get_object_or_404(Product, id=pk)
    data = cartData(request)
    cartItems = data['cartItems']
    # Safely get the first related ProductImage description (if any)
    first_image = product.images.first()
    description = first_image.description if first_image else ''

    context = {'product': product, 'cartItems':cartItems, 'description': description}
    return render(request, 'store/product.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    # Ensure Customer exists for this authenticated user
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
    else:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def category(request, pro):
    pro = pro.replace('-', ' ')

    try:
        category = Category.objects.get(name__iexact=pro)
        products = Product.objects.filter(category=category)
        
    except:
        messages.error(request, 'Category does not exist!')
        return redirect('store')
    
    return render(request, 'store/category.html', {'category': category, 'products': products})

def processOrder(request):  
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        

        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == (order.get_cart_total ):
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    return JsonResponse('Payment complete!', safe=False)

def customer_care(request):
    context = {}
    return render(request, 'store/customer_care.html', context)
