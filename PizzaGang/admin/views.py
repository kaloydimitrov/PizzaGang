from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView
from .forms import PizzaForm, OfferForm
from PizzaGang.main.models import Pizza, Cart, CartItem, Order, Offer, OfferItem
from .decorators import allowed_groups

User = get_user_model()


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


@allowed_groups(['full_staff', 'order_staff'], redirect_url=reverse_lazy('home'))
def MakeOrderFinishedView(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.is_finished = True
    order.save()

    return redirect('show_all_orders')


@method_decorator(allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home')), name='dispatch')
class CreatePizzaView(CreateView):
    model = Pizza
    form_class = PizzaForm
    template_name = 'pizza/create_pizza.html'
    success_url = reverse_lazy('home')


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


@method_decorator(allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home')), name='dispatch')
class DeletePizzaView(DeleteView):
    model = Pizza
    template_name = 'pizza/delete_pizza.html'
    success_url = reverse_lazy('menu')


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


@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def CreateOfferView(request):
    in_progress_offer_list = Offer.objects.filter(in_progress=True)

    if in_progress_offer_list.count() >= 1:
        return redirect('edit_offer')

    offer = Offer()
    offer.save()

    return redirect('edit_offer')


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


@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def CreateItemOfferView(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)
    offer = Offer.objects.filter(in_progress=True).get()

    item = CartItem(pizza=pizza, offer=offer)
    item.save()

    return redirect('edit_offer')


@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def DeleteItemOfferView(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    item.delete()

    return redirect('edit_offer')


@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def PushOfferView(request):
    offer = Offer.objects.filter(in_progress=True).get()

    if not offer.name or not offer.image or not offer.final_price:
        return redirect('edit_offer')

    offer.in_progress = False
    offer.save()

    return redirect('show_offers_settings')


@allowed_groups(['full_staff', 'settings_staff'], redirect_url=reverse_lazy('home'))
def DeleteOfferView(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    items = CartItem.objects.filter(offer=offer)

    offer.delete()
    items.delete()

    return redirect('show_offers_settings')


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
