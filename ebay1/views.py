from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import OrderItem, Product, Category, Cart, CartItem, Order, Review


def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "home.html", {"products": products, "categories": categories})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product_detail.html", {"product": product})


def category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.filter(is_active=True)
    return render(request, "category_products.html", {"category": category, "products": products})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(customer=request.user, defaults={"created_at": timezone.now()})
    cart.add_to_cart(product)
    return redirect("cart_detail")


def cart_detail(request):
    cart = get_object_or_404(Cart, customer=request.user)
    return render(request, "cart_detail.html", {"cart": cart})


def checkout(request):
    cart = get_object_or_404(Cart, customer=request.user)
    if request.method == "POST":
        order = Order.objects.create(
            customer=request.user,
            shipping_address=request.POST["shipping_address"],
            total_price=cart.get_total_price()
        )
        for item in cart.cart_items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart.cart_items.all().delete()
        return redirect("order_success")
    return render(request, "checkout.html")


def order_success(request):
    return render(request, "order_success.html")
