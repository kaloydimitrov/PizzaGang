from .models import Cart, CartItem, OfferItem


def get_cart_items_count(request):
    cart_items_count = 0

    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)

        pizza_items_count = CartItem.objects.filter(cart=cart).count()

        offer_items_count = 0
        offer_items = OfferItem.objects.filter(cart=cart)
        offers = []
        for offer_item in offer_items:
            offers.append(offer_item.offer)
        for offer in offers:
            offer_items = CartItem.objects.filter(offer=offer)
            offer_items_count += offer_items.count()

        cart_items_count = pizza_items_count + offer_items_count

    return {'cart_items_count': cart_items_count, 'user': request.user}
