from django.urls import path, include
from .views import HomeView, MenuView, \
                    ShowCartView, DeleteFromCartView, SelectItemSizeView, CreateOrderView, AddToCartView, \
                    ProductsView, AboutView

urlpatterns = (
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductsView.as_view(), name='products'),
    path('about/', AboutView.as_view(), name='about'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('cart/', include([
        path('add/<int:pk>/', AddToCartView, name='add_to_cart'),
        path('delete/<int:pk>/', DeleteFromCartView, name='delete_from_cart'),
        path('select-size/<int:pk>/', SelectItemSizeView, name='select_item_size'),
        path('show/', ShowCartView, name='show_cart'),
    ])),
    path('orders/', include([
        path('create/', CreateOrderView, name='create_order'),
    ])),
)
