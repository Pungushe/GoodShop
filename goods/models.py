from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.ImageField(upload_to="products", verbose_name="Изображение")
    marked_price = models.PositiveIntegerField(verbose_name="Цена")
    selling_price = models.PositiveIntegerField(verbose_name="Цена продажи")
    description = models.TextField(verbose_name="Описание")
    warranty = models.CharField(max_length=300, null=True, blank=True, verbose_name="Гарантия")
    return_policy = models.CharField(max_length=300, null=True, blank=True, verbose_name="Политка возврата")
    view = models.PositiveIntegerField(verbose_name="Обзоры")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + "CartProduct: " + str(self.id)

    class Meta:
        verbose_name = "Продукт корзины"
        verbose_name_plural = "Продукты корзины"


ORDER_STATUS = (
    ("Заказ получен", "Заказ получен"),
    ("Заказ обрабатывается", "Заказ обрабатывается"),
    ("Заказ в пути", "Заказ в пути"),
    ("Заказ выполнен", "Заказ выполнен"),
    ("Заказ отменен", "Заказ отменен"),
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
