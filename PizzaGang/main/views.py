from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .forms import SignUpForm, UserEditForm, PizzaForm, ProfileEditForm, OfferForm
from .models import Pizza, Profile, Cart, CartItem, Order, Offer
from .filters import PizzaOrderFilter

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'index.html'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'authentication/sign_up.html'
    success_url = reverse_lazy('sign_in')

    # TODO: These fields should be updated in forms.py
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        form.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
        return form


class SignInView(LoginView):
    template_name = 'authentication/sign_in.html'
    next_page = reverse_lazy('home')
    form_class = AuthenticationForm

    # TODO: These fields should be updated in forms.py
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['username'].widget.attrs['placeholder'] = 'Username'
        form.fields['password'].widget.attrs['placeholder'] = 'Password'
        return form


class SignOutView(LogoutView):
    next_page = reverse_lazy('home')


def UserShowView(request, pk):
    user = User.objects.get(pk=pk)

    context = {
        'user': user
    }

    return render(request, 'user_info/show_info.html', context)


def UserEditView(request, pk):
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user_view_link = f'/user-info/show/{pk}/'
            return redirect(user_view_link)
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user
    }

    return render(request, 'user_info/edit_info.html', context)


def UserAddressView(request, pk):
    pass


def MenuView(request):
    pizza_list = Pizza.objects.all()
    pizza_filter = PizzaOrderFilter(request.GET, queryset=pizza_list)

    context = {
        'pizza_list': pizza_list,
        'pizza_filter': pizza_filter,
    }

    return render(request, 'pizza/menu.html', context)


def AddToCartView(request, pk):
    pizza = Pizza.objects.get(pk=pk)
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    # Adds new pizza in cart
    cart_item = CartItem(cart=cart, pizza=pizza, final_price=pizza.price)
    cart_item.save()

    # Checks for duplication
    duplication_count = CartItem.objects.filter(cart=cart, pizza=pizza).count()
    pizza.duplication_count = duplication_count
    pizza.save()

    return redirect('menu')


def SelectItemSizeView(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)

    # big_button
    multiply_number = 1

    if 'small_button' in request.POST:
        cart_item.is_small = True
        cart_item.is_big = False
        cart_item.is_large = False

        multiply_number = 0.75

    elif 'big_button' in request.POST:
        cart_item.is_small = False
        cart_item.is_big = True
        cart_item.is_large = False

    elif 'large_button' in request.POST:
        cart_item.is_small = False
        cart_item.is_big = False
        cart_item.is_large = True

        multiply_number = 1.25

    if cart_item.is_half_price:
        cart_item.final_price = (cart_item.pizza.price / 2) * multiply_number
    else:
        cart_item.final_price = cart_item.pizza.price * multiply_number

    cart_item.save()

    if cart_item.offer:
        return redirect('edit_offer')
    return redirect('show_cart')


def DeleteFromCartView(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    pizza = cart_item.pizza
    user = request.user
    cart = Cart.objects.get(user=user)

    # Removes pizza from cart
    cart_item.delete()

    # Returns to menu if there are no pizzas in cart
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items.count() == 0:
        return redirect('menu')

    # Checks for duplication
    duplication_count = CartItem.objects.filter(cart=cart, pizza=pizza).count()
    pizza.duplication_count = duplication_count
    pizza.save()

    return redirect('show_cart')


def ShowCartView(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    cart_items = CartItem.objects.filter(cart=cart).order_by('created_at')

    # Pizza half price
    if cart_items.count() >= 2:
        cart_item = cart_items.order_by('pizza__price')[0]

        if not cart_item.is_half_price:
            cart_item.final_price = cart_item.final_price / 2
            cart_item.is_half_price = True
            cart_item.save()

    if cart_items.count() == 1 and cart_items.get().is_half_price:
        cart_item = cart_items.get()
        cart_item.is_small = False
        cart_item.is_big = True
        cart_item.is_large = False
        cart_item.is_half_price = False
        cart_item.final_price = cart_item.pizza.price
        cart_item.save()

    elif cart_items.filter(is_half_price=True).count() > 1:
        cart_item = cart_items.order_by('pizza__price')[1]
        cart_item.is_small = False
        cart_item.is_big = True
        cart_item.is_large = False
        cart_item.is_half_price = False
        cart_item.final_price = cart_item.pizza.price
        cart_item.save()

    # Calculates total price
    cart_total_price = 0
    for item in cart_items:
        cart_total_price += item.final_price

    cart.total_price = cart_total_price
    cart.save()

    context = {
        'cart_items': cart_items,
        'cart_total_price': cart.total_price
    }

    return render(request, 'cart/show_cart.html', context)


def CreateOrderView(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    cart_items = CartItem.objects.filter(cart=cart)
    order_items = []
    for item in cart_items:
        size = 'None'
        if item.is_small:
            size = 'SM'
        elif item.is_big:
            size = 'BI'
        elif item.is_large:
            size = 'LA'

        order_items.append(f"{item.pizza.name} {size}, {item.final_price}")
    order_items_string = ' • '.join(order_items)

    print(cart.total_price)
    order = Order(user=user, cart_items=order_items_string, total_price=cart.total_price)
    order.save()

    cart_items.delete()

    user_orders_link = f'/orders/show/{user.pk}/'
    return redirect(user_orders_link)


def ShowOrdersUserView(request, pk):
    user = User.objects.get(pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    active_orders = Order.objects.filter(user=user, is_finished=False)

    context = {
        'orders': orders,
        'active_orders': active_orders
    }

    return render(request, 'orders/show_user_orders.html', context)


def ShowOrdersAllView(request):
    orders = Order.objects.filter(is_finished=False).order_by('created_at')
    orders_finished = Order.objects.filter(is_finished=True)

    context = {
        'orders': orders,
        'orders_finished': orders_finished
    }

    return render(request, 'orders/show_all_orders.html', context)


def MakeOrderFinishedView(request, pk):
    order = Order.objects.get(pk=pk)
    order.is_finished = True
    order.save()

    return redirect('show_all_orders')


def DeleteOrderView(request, pk):
    order = Order.objects.get(pk=pk)
    order.delete()

    return redirect('menu')


def CreatePizzaView(request):
    if request.method == 'POST':
        form = PizzaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PizzaForm

    context = {
        'form': form,
    }

    return render(request, 'pizza/create_pizza.html', context)


def EditPizzaView(request, pk):
    pizza = Pizza.objects.get(pk=pk)

    if request.method == 'POST':
        form = PizzaForm(request.POST, request.FILES, instance=pizza)
        if form.is_valid():
            form.save()
            return redirect('show_pizza_settings')
    else:
        form = PizzaForm(instance=pizza)

    context = {
        'form': form,
        'pizza': pizza
    }

    return render(request, 'pizza/edit_pizza.html', context)


class DeletePizzaView(DeleteView):
    model = Pizza
    template_name = 'pizza/delete_pizza.html'
    success_url = reverse_lazy('menu')


def ShowUsersSettingsView(request):
    username_filter = request.GET.get('username', '')
    user_list = User.objects.filter(username__icontains=username_filter)

    context = {
        'user_list': user_list,
        'username_filter': username_filter
    }

    return render(request, 'admin/admin_settings_users.html', context)


def ShowPizzaSettingsView(request):
    name_filter = request.GET.get('name', '')
    pizza_list = Pizza.objects.filter(name__icontains=name_filter)

    context = {
        'pizza_list': pizza_list,
        'name_filter': name_filter
    }

    return render(request, 'admin/admin_settings_pizza.html', context)


def ShowOrdersSettingsView(request):
    username_filter = request.GET.get('username', '')
    order_list = Order.objects.filter(user__username__icontains=username_filter)

    context = {
        'order_list': order_list,
        'username_filter': username_filter
    }

    return render(request, 'admin/admin_settings_orders.html', context)


def ShowOffersSettingsView(request):
    return render(request, 'admin/admin_settings_offers.html')


def CreateOfferView(request):
    offer = Offer()
    offer.save()

    return redirect('edit_offer')


def EditOfferView(request):
    pizza_list = Pizza.objects.all()
    offer = Offer.objects.filter(in_progress=True).get()
    item_list = CartItem.objects.filter(offer=offer)

    offer_total_price = 0
    for item in item_list:
        offer_total_price += item.final_price
    offer.final_price = offer_total_price
    offer.save()

    if request.method == 'POST':
        form = OfferForm(instance=offer)
        if form.is_valid():
            form.save()
            return redirect('show_offers_settings')

    form = OfferForm(instance=offer)

    context = {
        'pizza_list': pizza_list,
        'item_list': item_list,
        'form': form,
        'offer_total_price': offer_total_price
    }

    return render(request, 'offer/edit_offer.html', context)


def CreateItemOfferView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)
    offer = Offer.objects.filter(in_progress=True).get()

    item = CartItem(pizza=pizza, final_price=pizza.price, offer=offer)
    item.save()

    return redirect('edit_offer')


def DeleteItemOfferView(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    item.delete()

    return redirect('edit_offer')
