from .models import Cart, CartItem


def get_cart_items_count(request):
    cart_items_count = 0

    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_count = cart_items.count()

    return {'cart_items_count': cart_items_count, 'user': request.user}
