from .models import Cart, CartItem


def get_cart_items_count(request):
    user = request.user
    cart = Cart.objects.get(user=user)

    cart_items = CartItem.objects.filter(cart=cart)
    cart_items_count = cart_items.count()

    return {'cart_items_count': cart_items_count}
