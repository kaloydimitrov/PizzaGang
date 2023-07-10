from django.urls import path, include
from .views import HomeView, SignUpView, SignInView, SignOutView, MenuView, UserEditView, UserAddressView, \
                    CreatePizzaView, EditPizzaView, DeletePizzaView, UserShowView, AddToCartView, \
                    ShowCartView, DeleteFromCartView

urlpatterns = (
    path('', HomeView.as_view(), name='home'),
    path('identity/', include([
        path('sign-up/', SignUpView.as_view(), name='sign_up'),
        path('sign-in/', SignInView.as_view(), name='sign_in'),
        path('sign-out/', SignOutView.as_view(), name='sign_out')
    ])),
    path('user-info/', include([
        path('show/<int:pk>/', UserShowView, name='show_user'),
        path('edit/<int:pk>/', UserEditView, name='edit_user'),
    ])),
    path('menu/', MenuView, name='menu'),
    path('pizza/', include([
        path('create/', CreatePizzaView, name='create_pizza'),
        path('edit/<int:pk>/', EditPizzaView, name='edit_pizza'),
        path('delete/<int:pk>/', DeletePizzaView.as_view(), name='delete_pizza')
    ])),
    path('cart/', include([
        path('add/<int:pk>', AddToCartView, name='add_to_cart'),
        path('delete/<int:pk>/', DeleteFromCartView, name='delete_from_cart'),
        path('show/', ShowCartView, name='show_cart'),
    ]))
)
