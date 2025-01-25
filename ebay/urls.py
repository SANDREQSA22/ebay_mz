from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("category/<int:pk>/", views.category_products, name="category_products"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/", views.order_success, name="order_success"),
]
