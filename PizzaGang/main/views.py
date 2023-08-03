from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .forms import SignUpForm, UserEditForm, PizzaForm, ProfileEditForm, OfferForm
from .models import Pizza, Profile, Cart, CartItem, Order, Offer, OfferItem, Review, ProductImage
from .filters import PizzaOrderFilter
from .decorators import allowed_groups

User = get_user_model()


def HomeView(request):
    offer_list = Offer.objects.filter(in_progress=False, is_active=True)
    review_list = Review.objects.all().order_by('-created_at')
    pizza_list_veggie = Pizza.objects.filter(Q(is_vege=True) & ~Q(is_offer=True) & ~Q(is_special=True))
    pizza_list_offer = Pizza.objects.filter(Q(is_offer=True) & ~Q(is_vege=True) & ~Q(is_special=True))
    pizza_list_special = Pizza.objects.filter(Q(is_special=True) & ~Q(is_vege=True) & ~Q(is_offer=True))

    context = {
        'offer_list': offer_list,
        'review_list': review_list,
        'pizza_list_veggie': pizza_list_veggie,
        'pizza_list_offer': pizza_list_offer,
        'pizza_list_special': pizza_list_special
    }

    return render(request, 'index.html', context)


class ProductsView(ListView):
    model = ProductImage
    template_name = 'products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_products'] = True
        return context


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_about'] = True
        return context


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


@login_required(login_url=reverse_lazy('sign_in'))
def UserShowView(request, pk):
    if request.user.pk != pk:
        return redirect('home')

    user = get_object_or_404(User, pk=pk)

    context = {
        'user': user
    }

    return render(request, 'user_info/show_info.html', context)


def UserShowPublicView(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        user_view_link = f'/user-info/show/{pk}/'
        return redirect(user_view_link)

    review_list = Review.objects.filter(user=user)

    context = {
        'user': user,
        'review_list': review_list
    }

    return render(request, 'user_info/show_public_info.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
def UserEditView(request, pk):
    if request.user.pk != pk:
        return redirect('home')

    user = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(Profile, user=user)

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


# TODO: Make it work with CBV
# @login_required(login_url=reverse_lazy('sign_in'))
class UserAddressView(TemplateView):
    template_name = 'user_info/show_address.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


def MenuView(request):
    pizza_list = Pizza.objects.all()
    pizza_filter = PizzaOrderFilter(request.GET, queryset=pizza_list)

    context = {
        'pizza_list': pizza_list,
        'pizza_filter': pizza_filter,
        'in_menu': True
    }

    return render(request, 'pizza/menu.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
def AddToCartView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)
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


@login_required(login_url=reverse_lazy('sign_in'))
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


@login_required(login_url=reverse_lazy('sign_in'))
def DeleteFromCartView(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    pizza = cart_item.pizza
    user = request.user
    cart = get_object_or_404(Cart,user=user)

    # Removes pizza from cart
    cart_item.delete()

    # Returns to menu if there are no items in cart
    cart_items = CartItem.objects.filter(cart=cart).count() + OfferItem.objects.filter(cart=cart).count()
    if cart_items == 0:
        return redirect('menu')

    # Checks for duplication
    duplication_count = CartItem.objects.filter(cart=cart, pizza=pizza).count()
    pizza.duplication_count = duplication_count
    pizza.save()

    return redirect('show_cart')


@login_required(login_url=reverse_lazy('sign_in'))
def ShowCartView(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    cart_items = CartItem.objects.filter(cart=cart).order_by('created_at')
    offer_items = OfferItem.objects.filter(cart=cart)

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

    for item in offer_items:
        cart_total_price += item.offer.final_price

    cart.total_price = cart_total_price
    cart.save()

    context = {
        'cart_items': cart_items,
        'cart_total_price': cart.total_price,
        'offer_items': offer_items
    }

    return render(request, 'cart/show_cart.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
def CreateOrderView(request):
    if not request.user.profile.address:
        return redirect('show_user_address')

    user = request.user
    cart = get_object_or_404(Cart, user=user)

    order_items = []

    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        size = 'None'
        if item.is_small:
            size = 'SMALL'
        elif item.is_big:
            size = 'BIG'
        elif item.is_large:
            size = 'LARGE'

        order_items.append(f"{item.pizza.name} - {size}")
        item.delete()

    offer_items = OfferItem.objects.filter(cart=cart)
    for offer_item in offer_items:
        cart_items = CartItem.objects.filter(offer=offer_item.offer)
        for item in cart_items:
            size = 'None'
            if item.is_small:
                size = 'SMALL'
            elif item.is_big:
                size = 'BIG'
            elif item.is_large:
                size = 'LARGE'

            order_items.append(f"{item.pizza.name} - {size}")
        offer_item.delete()

    order_items_string = ' • '.join(order_items)

    order = Order(user=user, cart_items=order_items_string, total_price=cart.total_price)
    order.save()

    user_orders_link = f'/orders/show/{user.pk}/'
    return redirect(user_orders_link)


@login_required(login_url=reverse_lazy('sign_in'))
def ShowOrdersUserView(request, pk):
    user = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    active_orders = Order.objects.filter(user=user, is_finished=False)

    context = {
        'orders': orders,
        'active_orders': active_orders
    }

    return render(request, 'orders/show_user_orders.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'order_staff'], redirect_url=reverse_lazy('home'))
def ShowOrdersAllView(request):
    orders = Order.objects.filter(is_finished=False).order_by('created_at')
    orders_finished = Order.objects.filter(is_finished=True)

    context = {
        'orders': orders,
        'orders_finished': orders_finished
    }

    return render(request, 'orders/show_all_orders.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'order_staff'], redirect_url=reverse_lazy('home'))
def MakeOrderFinishedView(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.is_finished = True
    order.save()

    return redirect('show_all_orders')


@login_required(login_url=reverse_lazy('sign_in'))
def DeleteOrderView(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()

    return redirect('menu')


# TODO: Make it work with CBV
# @login_required(login_url=reverse_lazy('sign_in'))
# @allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
class CreatePizzaView(CreateView):
    model = Pizza
    form_class = PizzaForm
    template_name = 'pizza/create_pizza.html'
    success_url = reverse_lazy('home')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def EditPizzaView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)

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


# TODO: Make it work with CBV
# @login_required(login_url=reverse_lazy('sign_in'))
# @allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
class DeletePizzaView(DeleteView):
    model = Pizza
    template_name = 'pizza/delete_pizza.html'
    success_url = reverse_lazy('menu')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowUsersSettingsView(request):
    username_filter = request.GET.get('username', '')
    user_list = User.objects.filter(username__icontains=username_filter)

    context = {
        'user_list': user_list,
        'username_filter': username_filter
    }

    return render(request, 'admin/admin_settings_users.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowPizzaSettingsView(request):
    name_filter = request.GET.get('name', '')
    pizza_list = Pizza.objects.filter(name__icontains=name_filter)

    context = {
        'pizza_list': pizza_list,
        'name_filter': name_filter
    }

    return render(request, 'admin/admin_settings_pizza.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowOrdersSettingsView(request):
    username_filter = request.GET.get('username', '')
    order_list = Order.objects.filter(user__username__icontains=username_filter)

    context = {
        'order_list': order_list,
        'username_filter': username_filter
    }

    return render(request, 'admin/admin_settings_orders.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowOffersSettingsView(request):
    name_filter = request.GET.get('name', '')
    offer_list = Offer.objects.filter(name__icontains=name_filter, in_progress=False)
    in_progress = True if Offer.objects.filter(in_progress=True).count() >= 1 else False

    context = {
        'offer_list': offer_list,
        'in_progress': in_progress
    }

    return render(request, 'admin/admin_settings_offers.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def CreateOfferView(request):
    in_progress_offer_list = Offer.objects.filter(in_progress=True)

    if in_progress_offer_list.count() >= 1:
        return redirect('edit_offer')

    offer = Offer()
    offer.save()

    return redirect('edit_offer')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def EditOfferView(request):
    name_filter = request.GET.get('name', '')
    pizza_list = Pizza.objects.filter(name__icontains=name_filter)
    offer = Offer.objects.filter(in_progress=True).get()
    item_list = CartItem.objects.filter(offer=offer)

    offer_total_price = 0
    for item in item_list:
        offer_total_price += item.final_price
    offer.total_price = offer_total_price

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('edit_offer')
    else:
        form = OfferForm(instance=offer)

    context = {
        'pizza_list': pizza_list,
        'item_list': item_list,
        'form': form,
        'offer': offer
    }

    return render(request, 'offer/edit_offer.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def CreateItemOfferView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)
    offer = Offer.objects.filter(in_progress=True).get()

    item = CartItem(pizza=pizza, final_price=pizza.price, offer=offer)
    item.save()

    return redirect('edit_offer')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def DeleteItemOfferView(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    item.delete()

    return redirect('edit_offer')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def PushOfferView(request):
    offer = Offer.objects.filter(in_progress=True).get()

    if not offer.name or not offer.image or not offer.final_price:
        return redirect('edit_offer')

    offer.in_progress = False
    offer.save()

    return redirect('show_offers_settings')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def DeleteOfferView(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    items = CartItem.objects.filter(offer=offer)

    offer.delete()
    items.delete()

    return redirect('show_offers_settings')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def MakeOfferActiveInactiveView(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    if 'active' in request.POST:
        offer.is_active = True
    elif 'inactive' in request.POST:
        offer.is_active = False

    offer.save()
    return redirect('show_offers_settings')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def CreateOfferItemView(request, pk):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    offer = get_object_or_404(Offer, pk=pk)

    offer_item = OfferItem(cart=cart, offer=offer)
    offer_item.save()

    return redirect('home')


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def DeleteOfferItemView(request, pk):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    offer_item = get_object_or_404(OfferItem, pk=pk)
    offer_item.delete()

    cart_items = CartItem.objects.filter(cart=cart).count() + OfferItem.objects.filter(cart=cart).count()
    if cart_items == 0:
        return redirect('menu')

    return redirect('show_cart')


@login_required(login_url=reverse_lazy('sign_in'))
def CreateReviewView(request):
    user = request.user

    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        review = Review(user=user, text=text, rating=rating)
        review.save()

        user_reviews_link = f'/review/show/{user.pk}/'
        return redirect(user_reviews_link)

    return render(request, 'review/create_review.html')


@login_required(login_url=reverse_lazy('sign_in'))
def ShowReviewsUserView(request, pk):
    user = get_object_or_404(User, pk=pk)
    review_list = Review.objects.filter(user=user).order_by('-created_at')

    context = {
        'review_list': review_list
    }

    return render(request, 'review/show_user_reviews.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
def DeleteReviewView(request, pk):
    user = request.user
    review = get_object_or_404(Review, pk=pk)
    review.delete()

    user_reviews_link = f'/review/show/{user.pk}/'
    return redirect(user_reviews_link)
