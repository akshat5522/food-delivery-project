from django.shortcuts import render, redirect
from .models import * 
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
import razorpay
from django.conf import settings 
from django.contrib.auth.decorators import login_required


def base(request):
    return render(request, 'base.html')

def home(request):
    pizzas = Pizza.objects.all()
    return render(request, "home.html", {"pizzas":pizzas})

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            user_obj = User.objects.filter(username = username)
            if not user_obj.exists():
                messages.warning(request, "Invalid username or password.")
                return redirect("login")

            user_obj = authenticate(username = username, password = password)
            
            if user_obj:
                login(request, user_obj)
                return redirect("home")

            messages.error(request, "Wrong password.")

            return redirect("login")
        
        except Exception as e:
            messages.error(request, "Something went wrong.")

            return redirect("register")
        
    return render(request, "login.html")

def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            user_obj = User.objects.filter(username = username)
            if user_obj.exists():
                messages.warning(request, "This username is already in use.")
                return redirect("register")

            user_obj = User.objects.create_user(username = username, password = password)
            messages.success(request, "Account created successfully.")
            return redirect("login")
        
        except Exception as e:
            messages.error(request, "Something went wrong.")

            return redirect("register")

    return render(request, "register.html")

@login_required(login_url='/login_page/') #redirect when user is not logged in
def add_cart(request, pizza_uid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid = pizza_uid)
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_items = CartItems.objects.create(
        cart = cart,
        pizza = pizza_obj
    )

    return redirect('/home/')

@login_required(login_url='/login_page/')
def cart(request):
    cart = Cart.objects.get(is_paid = False, user = request.user)
    client = razorpay.Client(auth = (settings.RAZOR_KEY, settings.SECRET))
    payment = client.order.create({'amount': cart.get_cart_total() * 100, 'currency' : 'INR', 'payment_capture' : 1})
    cart.razor_pay_order_id= payment['id']
    cart.save()

    print('******')
    print(payment)
    print('******')
    return render(request, "cart.html", {"carts" : cart, 'payment' : payment})

@login_required(login_url='/login_page/')
def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid = cart_item_uid).delete()

        return redirect('/cart/')
    except  Exception as e:
        print(e)

@login_required(login_url='/login_page/')
def orders(request):
    orders = Cart.objects.filter(is_paid = True, user = request.user)
    return render(request, 'orders.html', {'orders' : orders})

@login_required(login_url='/login_page/')
def success(request):
    order_id = request.GET.get('order_id')

    try:
        cart = Cart.objects.get(razor_pay_order_id=order_id)
        cart.is_paid = True
        cart.save()
    except Cart.DoesNotExist:
        print("Cart not found for order_id:", order_id)

    return redirect('/orders/')


# def process_payment(request):
#     return redirect