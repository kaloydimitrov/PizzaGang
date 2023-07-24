from django.urls import path, include
from .views import HomeView, SignUpView, SignInView, SignOutView, MenuView, UserEditView, UserAddressView, \
                    CreatePizzaView, EditPizzaView, DeletePizzaView, UserShowView, AddToCartView, \
                    ShowCartView, DeleteFromCartView, SelectItemSizeView, CreateOrderView, ShowOrdersUserView, \
                    ShowOrdersAllView, MakeOrderFinishedView, ShowUsersSettingsView, ShowPizzaSettingsView, \
                    ShowOrdersSettingsView, DeleteOrderView, ShowOffersSettingsView, CreateOfferView, \
                    EditOfferView, CreateItemOfferView, DeleteItemOfferView, PushOfferView, DeleteOfferView, \
                    MakeOfferActiveInactiveView, CreateOfferItemView, DeleteOfferItemView

urlpatterns = (
    path('', HomeView, name='home'),
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
        path('add/<int:pk>/', AddToCartView, name='add_to_cart'),
        path('delete/<int:pk>/', DeleteFromCartView, name='delete_from_cart'),
        path('select-size/<int:pk>/', SelectItemSizeView, name='select_item_size'),
        path('show/', ShowCartView, name='show_cart'),
    ])),
    path('orders/', include([
        path('create/', CreateOrderView, name='create_order'),
        path('delete/<int:pk>/', DeleteOrderView, name='delete_order'),
        path('show/<int:pk>/', ShowOrdersUserView, name='show_user_orders'),
        path('show-all/', ShowOrdersAllView, name='show_all_orders'),
        path('make-finished/<int:pk>/', MakeOrderFinishedView, name='make_finished_order')
    ])),
    path('offer/', include([
        path('create/', CreateOfferView, name='create_offer'),
        path('edit/', EditOfferView, name='edit_offer'),
        path('create-item/<int:pk>/', CreateItemOfferView, name='create_item_offer'),
        path('delete-item/<int:pk>/', DeleteItemOfferView, name='delete_item_offer'),
        path('push/', PushOfferView, name='push_offer'),
        path('delete/<int:pk>/', DeleteOfferView, name='delete_offer'),
        path('make-active/<int:pk>/', MakeOfferActiveInactiveView, name='make_active_inactive_offer'),
        path('create-offer-item/<int:pk>/', CreateOfferItemView, name='create_offer_item'),
        path('delete-offer-item/<int:pk>/', DeleteOfferItemView, name='delete_offer_item')
    ])),
    path('pizzagang-admin/', include([
        path('show/', ShowOrdersAllView, name='show_admin'),
        path('settings/', include([
            path('users/', ShowUsersSettingsView, name='show_users_settings'),
            path('pizza/', ShowPizzaSettingsView, name='show_pizza_settings'),
            path('orders/',ShowOrdersSettingsView, name='show_orders_settings'),
            path('offers/', ShowOffersSettingsView, name='show_offers_settings')
        ]))
    ]))
)
