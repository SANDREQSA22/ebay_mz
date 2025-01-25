from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class Customer(models.Model):
    username = models.CharField(max_length=100, verbose_name="იუზერნეიმი")
    first_name = models.CharField(max_length=100, verbose_name="სახელი", default="")
    last_name = models.CharField(max_length=100, verbose_name="გვარი", default="")
    email = models.EmailField("ელ.ფოსტის მისამართი", unique=True)
    is_active = models.BooleanField("აქტიურია", default=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    class Meta:
        ordering = ("-id",)
        verbose_name = "მომხმარებელი"
        verbose_name_plural = "მომხმარებლები"


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="კატეგორიის დასახელება")
    description = models.TextField(verbose_name="კატეგორიის აღწერა", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "კატეგორია"
        verbose_name_plural = "კატეგორიები"


class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name="დასახელება")
    description = models.TextField(verbose_name="აღწერა")
    seller = models.ForeignKey(Customer, related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    listing_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name="products", on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True, verbose_name="აქტიური")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-listing_date",)
        verbose_name = "პროდუქტი"
        verbose_name_plural = "პროდუქტები"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, related_name="carts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cart #{self.id} - {self.customer.get_full_name()}"

    def add_to_cart(self, product, quantity=1):
        if product.quantity < quantity:
            raise ValidationError("საკმარისი რაოდენობა არ არის")

        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            cart=self,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        product.quantity -= quantity
        product.save()

        return cart_item

    def get_total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())


class CartItem(models.Model):
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} - {self.quantity} pcs"

    def total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False, verbose_name="გადახდილია")
    shipping_address = models.TextField(verbose_name="მიტანის მისამართი")

    def __str__(self):
        return f"Order #{self.id} - {self.customer.get_full_name()}"

    def calculate_total(self):
        self.total_price = sum(item.total_price() for item in self.order_items.all())
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.title} - {self.quantity} pcs"

    def total_price(self):
        return self.quantity * self.product.price


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5, verbose_name="რეიტინგი")
    comment = models.TextField(verbose_name="კომენტარი", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.get_full_name()} for {self.product.title}"

