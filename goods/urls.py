from django.urls import path
from .views import *

app_name = 'goods'

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("all-products/", AllProductsView.as_view(), name="all_products"),
    path("product/<slug:slug>", ProductDetailView.as_view(), name="product_detail"),

    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="add_cart"),
    path("my-cart/", MyCartView.as_view(), name="my_cart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="manage_cart"),
    path("empty-cart/", EmptyCartView.as_view(), name="empty_cart"),

    path("check-out/", CheckoutView.as_view(), name="check_out"),
    path("register/", RegistrationView.as_view(), name="registration"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/order-<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("search/", SearchView.as_view(), name="search"),

]

  