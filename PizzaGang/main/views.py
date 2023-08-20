from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from PizzaGang.main.models import Pizza, Cart, CartItem, Order, OfferItem, Review, ProductImage, Offer
from .filters import PizzaOrderFilter

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

    if cart_item.cart:
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


@login_required(login_url=reverse_lazy('sign_in'))
def ShowCartView(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    cart_items = CartItem.objects.filter(cart=cart).order_by('created_at')
    offer_items = OfferItem.objects.filter(cart=cart)

    # The function is described above
    calculates_BOGO_offer(cart_items, cart)

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
    cart_total_price = cart.total_price
    cart_items = CartItem.objects.filter(cart=cart)
    offer_items = OfferItem.objects.filter(cart=cart)

    order_items = []

    def add_to_order_items(order_item):
        size = None
        if order_item.is_small:
            size = 'SMALL'
        elif order_item.is_big:
            size = 'BIG'
        elif order_item.is_large:
            size = 'LARGE'

        order_items.append(f"{order_item.pizza.name} - {size}")

    for cart_item in cart_items:
        add_to_order_items(cart_item)
        cart_item.delete()

    for offer_item in offer_items:
        cart_items = CartItem.objects.filter(offer=offer_item.offer)
        for cart_item in cart_items:
            add_to_order_items(cart_item)

        offer_item.delete()

    order = Order(user=user, cart_items=' • '.join(order_items), total_price=cart_total_price)
    order.save()

    return redirect(f'/orders/show/{user.pk}/')
