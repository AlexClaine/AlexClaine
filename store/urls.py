from django.urls import path   
from . import views

urlpatterns = [
    path ('about/', views.about, name="about"),
    path('loginpage/', views.LoginPage, name="loginpage"),
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('category/<str:pro>', views.category, name="category"),
    path('register/', views.Register, name="register"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('product/<int:pk>/', views.ProductImage, name="product"),
    path('customer_care/', views.customer_care, name="customer_care"),
]