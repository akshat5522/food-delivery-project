from django.urls import path
from . import views

urlpatterns = [
    # path("", views.base, name='base'),
    path("home/", views.home, name='home'),
    path("login_page/", views.login_page, name='login'),
    path("register_page/", views.register_page, name='register'),
    path('add-cart/<pizza_uid>', views.add_cart, name='add_cart'),
    path("cart/", views.cart, name='cart'),
    path("remove_cart_items/<cart_item_uid>", views.remove_cart_items, name='remove_cart_items'),
    path('orders/', views.orders, name='orders'),
    path('success/', views.success, name='success')
]