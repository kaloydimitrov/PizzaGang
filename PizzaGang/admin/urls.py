from django.urls import path, include
from .views import CreatePizzaView, EditPizzaView, DeletePizzaView, ShowOrdersAllView, MakeOrderFinishedView, \
                    ShowUsersSettingsView, ShowPizzaSettingsView, ShowOrdersSettingsView, ShowOffersSettingsView, \
                    CreateOfferView, EditOfferView, CreateItemOfferView, DeleteItemOfferView, PushOfferView, \
                    DeleteOfferView, MakeOfferActiveInactiveView, CreateOfferItemView, DeleteOfferItemView

urlpatterns = (
    path('orders/', include([
        path('show-all/', ShowOrdersAllView, name='show_all_orders'),
        path('make-finished/<int:pk>/', MakeOrderFinishedView, name='make_finished_order')
    ])),
    path('pizza/', include([
        path('create/', CreatePizzaView.as_view(), name='create_pizza'),
        path('edit/<int:pk>/', EditPizzaView, name='edit_pizza'),
        path('delete/<int:pk>/', DeletePizzaView.as_view(), name='delete_pizza')
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
    path('pizza-gang-admin/', include([
        path('show/', ShowOrdersAllView, name='show_admin'),
        path('settings/', include([
            path('users/', ShowUsersSettingsView, name='show_users_settings'),
            path('pizza/', ShowPizzaSettingsView, name='show_pizza_settings'),
            path('orders/', ShowOrdersSettingsView, name='show_orders_settings'),
            path('offers/', ShowOffersSettingsView, name='show_offers_settings')
        ]))
    ]))
)
