from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DeleteView
from .forms import SignUpForm, UserEditForm, PizzaForm, ProfileEditForm, OfferForm, ReviewForm
from .models import Pizza, Profile, Cart, CartItem, Order, Offer, OfferItem, Review, ProductImage
from .filters import PizzaOrderFilter
from .decorators import allowed_groups

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        offer_list = Offer.objects.filter(in_progress=False, is_active=True).order_by('final_price', 'name')
        review_list = Review.objects.all().order_by('-created_at')
        pizza_list_veggie = Pizza.objects.filter(Q(is_vege=True) & ~Q(is_offer=True) & ~Q(is_special=True))
        pizza_list_offer = Pizza.objects.filter(Q(is_offer=True) & ~Q(is_vege=True) & ~Q(is_special=True))
        pizza_list_special = Pizza.objects.filter(Q(is_special=True) & ~Q(is_vege=True) & ~Q(is_offer=True))

        context = super().get_context_data(**kwargs)
        context['offer_list'] = offer_list
        context['review_list'] = review_list
        context['pizza_list_veggie'] = pizza_list_veggie
        context['pizza_list_offer'] = pizza_list_offer
        context['pizza_list_special'] = pizza_list_special
        context['in_home'] = True
        return context


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


class MenuView(ListView):
    template_name = 'pizza/menu.html'
    model = Pizza
    queryset = Pizza.objects.order_by('price', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_filter = PizzaOrderFilter(self.request.GET, queryset=self.queryset)
        context['pizza_filter'] = pizza_filter
        context['in_menu'] = True
        return context


# ------------------------------- User -------------------------------
class UserShowPublicView(View):
    @staticmethod
    def get(request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return redirect(f'/user-info/show/{pk}/')

        review_list = Review.objects.filter(user=user)

        context = {
            'review_list': review_list,
            'user': user
        }

        return render(request, 'user_info/show_public_info.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class UserShowView(View):
    @staticmethod
    def get(request, pk):
        if request.user.pk != pk:
            return redirect(f'/user-info/show/{request.user.pk}/')

        user = get_object_or_404(User, pk=pk)

        context = {
            'user': user
        }

        return render(request, 'user_info/show_info.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class UserAddressView(TemplateView):
    template_name = 'user_info/show_address.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class ShowOrdersUserView(ListView):
    model = Order
    template_name = 'orders/show_user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return Order.objects.filter(user=user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.request.user.pk)
        active_orders_count = Order.objects.filter(user=user, is_finished=False).count()
        context['active_orders_count'] = active_orders_count
        return context


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class DeleteOrderView(DeleteView):
    model = Order
    success_url = reverse_lazy('menu')


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class ShowReviewsUserView(ListView):
    template_name = 'review/show_user_reviews.html'
    context_object_name = 'review_list'

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return Review.objects.filter(user=user).order_by('-created_at')


@login_required(login_url=reverse_lazy('sign_in'))
def CreateReviewView(request):
    user = request.user

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        rating = request.POST.get('rating')
        if form.is_valid():
            review = Review(user=user, rating=rating, text=form.cleaned_data['text'])
            review.save()

            return redirect(f'/review/show/{user.pk}/')
    else:
        form = ReviewForm()

    context = {
        'form': form
    }

    return render(request, 'review/create_review.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class DeleteReviewView(DeleteView):
    model = Review
    template_name = 'review/show_user_reviews.html'

    def get_success_url(self):
        user_pk = self.request.user.pk
        return reverse('show_user_reviews', kwargs={'pk': user_pk})


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
            return redirect(f'/user-info/show/{pk}/')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user
    }

    return render(request, 'user_info/edit_info.html', context)


# ------------------------------- Core -------------------------------
@login_required(login_url=reverse_lazy('sign_in'))
def AddToCartView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    # Adds new pizza in cart
    cart_item = CartItem(cart=cart, pizza=pizza)
    cart_item.save()

    return redirect('menu')


@login_required(login_url=reverse_lazy('sign_in'))
def SelectItemSizeView(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)

    if cart_item.cart.user != request.user:
        return redirect('home')

    if 'small_button' in request.POST:
        cart_item.is_small = True
        cart_item.is_big = False
        cart_item.is_large = False

    elif 'big_button' in request.POST:
        cart_item.is_small = False
        cart_item.is_big = True
        cart_item.is_large = False

    elif 'large_button' in request.POST:
        cart_item.is_small = False
        cart_item.is_big = False
        cart_item.is_large = True

    cart_item.save()

    if cart_item.offer:
        return redirect('edit_offer')
    return redirect('show_cart')


@login_required(login_url=reverse_lazy('sign_in'))
def DeleteFromCartView(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    # Removes pizza from cart
    cart_item.delete()

    # Returns to menu if there are no items in cart
    cart_items = CartItem.objects.filter(cart=cart).count() + OfferItem.objects.filter(cart=cart).count()
    if cart_items == 0:
        return redirect('menu')

    return redirect('show_cart')


def calculates_BOGO_offer(cart_items, cart):
    if cart_items.count() == 1 and cart_items.get().is_half_price:
        cart_item = cart_items.get()
        cart_item.is_half_price = False
        cart_item.save()

    elif cart_items.count() >= 2:
        cheapest_cart_items = CartItem.objects.filter(cart=cart).order_by('pizza__price', 'pizza__name', 'pk')

        cheapest_cart_item = cheapest_cart_items[0]
        cheapest_cart_item.is_half_price = True
        cheapest_cart_item.save()

        if cart_items.filter(is_half_price=True).count() > 1:
            for cart_item in cart_items:
                if cart_item == cheapest_cart_item:
                    continue

                cart_item.is_half_price = False
                cart_item.save()


def calculates_cart_total_price(cart_items, offer_items, cart):
    cart_total_price = 0
    for item in cart_items:
        cart_total_price += item.final_price

    for item in offer_items:
        cart_total_price += item.offer.final_price

    cart.total_price = cart_total_price
    cart.save()


@login_required(login_url=reverse_lazy('sign_in'))
def ShowCartView(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    cart_items = CartItem.objects.filter(cart=cart).order_by('created_at')
    offer_items = OfferItem.objects.filter(cart=cart)

    # The functions are described above
    calculates_BOGO_offer(cart_items, cart)
    calculates_cart_total_price(cart_items, offer_items, cart)

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
    cart_items = CartItem.objects.filter(cart=cart)
    offer_items = OfferItem.objects.filter(cart=cart)

    order_items_list = []

    for item in cart_items:
        order_items_list.append(item)
        item.delete()

    for offer_item in offer_items:
        cart_items = CartItem.objects.filter(offer=offer_item.offer)
        for item in cart_items:
            order_items_list.append(item)

        offer_item.delete()

    order_items_string_list = []

    for item in order_items_list:
        size = None
        if item.is_small:
            size = 'SMALL'
        elif item.is_big:
            size = 'BIG'
        elif item.is_large:
            size = 'LARGE'

        order_items_string_list.append(f"{item.pizza.name} - {size}")

    order_items_string = ' • '.join(order_items_string_list)

    order = Order(user=user, cart_items=order_items_string, total_price=cart.total_price)
    order.save()

    user_orders_link = f'/orders/show/{user.pk}/'
    return redirect(user_orders_link)


# ------------------------------- Admin -------------------------------
@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'order_staff'], redirect_url=reverse_lazy('home'))
def ShowOrdersAllView(request):
    orders = Order.objects.filter(is_finished=False).order_by('created_at')
    orders_finished_count = Order.objects.filter(is_finished=True).count()

    context = {
        'orders': orders,
        'orders_finished_count': orders_finished_count
    }

    return render(request, 'orders/show_all_orders.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'order_staff'], redirect_url=reverse_lazy('home'))
def MakeOrderFinishedView(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.is_finished = True
    order.save()

    return redirect('show_all_orders')


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
@method_decorator(allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home')), name='dispatch')
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


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
@method_decorator(allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home')), name='dispatch')
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
        'username_filter': username_filter,
        'in_users': True
    }

    return render(request, 'admin/admin_settings_users.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowPizzaSettingsView(request):
    name_filter = request.GET.get('name', '')
    pizza_list = Pizza.objects.filter(name__icontains=name_filter)

    context = {
        'pizza_list': pizza_list,
        'name_filter': name_filter,
        'in_pizza': True
    }

    return render(request, 'admin/admin_settings_pizza.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowOrdersSettingsView(request):
    username_filter = request.GET.get('username', '')
    order_list = Order.objects.filter(user__username__icontains=username_filter)

    context = {
        'order_list': order_list,
        'username_filter': username_filter,
        'in_orders': True
    }

    return render(request, 'admin/admin_settings_orders.html', context)


@login_required(login_url=reverse_lazy('sign_in'))
@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def ShowOffersSettingsView(request):
    name_filter = request.GET.get('name', '')
    offer_list = Offer.objects.filter(name__icontains=name_filter, in_progress=False).order_by('-is_active', 'name')
    in_progress = True if Offer.objects.filter(in_progress=True).count() >= 1 else False

    context = {
        'offer_list': offer_list,
        'in_progress': in_progress,
        'in_offers': True
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
    pizza_list = Pizza.objects.filter(name__icontains=name_filter).order_by('price', 'name')
    offer = Offer.objects.filter(in_progress=True).get()
    item_list = CartItem.objects.filter(offer=offer).order_by('pizza__price', 'pizza__name')

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

    item = CartItem(pizza=pizza, final_price=pizza.final_price, offer=offer)
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
