from .models import Cart, CartItem, OfferItem


def get_cart_items_count(request):
    cart_items_count = 0

    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)

        pizza_items_count = CartItem.objects.filter(cart=cart).count()

        offer_items_count = 0
        offer_items = OfferItem.objects.filter(cart=cart)
        for offer_item in offer_items:
            offer_items_count += CartItem.objects.filter(offer=offer_item.offer).count()

        cart_items_count = pizza_items_count + offer_items_count

    return {'cart_items_count': cart_items_count, 'current_user': request.user}
