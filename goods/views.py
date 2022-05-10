from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from .forms import CheckOutForm, ProductForm, RegistrationForm, LoginForm
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q

from .models import *


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["myname"] = "Юрий"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 4)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context["product_list"] = product_list
        return context


class AllProductsView(EcomMixin, TemplateView):
    template_name = "all_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allcategories"] = Category.objects.all()
        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = "product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view += 1
        product.save()
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "add_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # получение товара по id
        product_id = self.kwargs['pro_id']
        # получение товара
        product_obj = Product.objects.get(id=product_id)

        # проверка есть ли корзина
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # проверка есть ли товар в корзине
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

                # проверка добавлен ли новый товар в корзину
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.selling_price, quantity=1,
                                                         subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                     rate=product_obj.selling_price, quantity=1,
                                                     subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        return context


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == 'rmv':
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("goods:my_cart")


class EmptyCartView(EcomMixin, View):

    def get(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("goods:my_cart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "my_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context["cart"] = cart
        return context


class CheckoutView(EcomMixin, CreateView):
    template_name = "check_out.html"
    form_class = CheckOutForm
    success_url = reverse_lazy("goods:profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/check-out/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context["cart"] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Получение заказа"
            del self.request.session['cart_id']
        else:
            return redirect('goods:my_cart')
        return super().form_valid(form)


class RegistrationView(CreateView):
    template_name = "registration.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("goods:my_cart")

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("goods:home")

    def form_valid(self, form):
        uname = form.cleaned_data.get('username')
        pword = form.cleaned_data['password']
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Неверные данные'})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('goods:home')


class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contact.html"


class ProfileView(EcomMixin, TemplateView):
    template_name = "profile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context["customer"] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class OrderDetailView(DetailView):
    template_name = "order_detail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("goods:profile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__contains=kw) | Q(description__icontains=kw) | Q(
                return_policy__icontains=kw))
        print(results)
        context["results"] = results
        return context
