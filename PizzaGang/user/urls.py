from django.urls import path, include
from .views import UserEditView, UserAddressView, ShowOrdersUserView, DeleteOrderView, CreateReviewView, \
                    UserShowView, ShowReviewsUserView, DeleteReviewView, UserShowPublicView


urlpatterns = (
    path('user-info/', include([
        path('show/<int:pk>/', UserShowView.as_view(), name='show_user'),
        path('show-public/<int:pk>/', UserShowPublicView.as_view(), name='show_user_public'),
        path('edit/<int:pk>/', UserEditView, name='edit_user'),
        path('address/', UserAddressView.as_view(), name='show_user_address')
    ])),
    path('orders/', include([
        path('delete/<int:pk>/', DeleteOrderView.as_view(), name='delete_order'),
        path('show/<int:pk>/', ShowOrdersUserView.as_view(), name='show_user_orders')
    ])),
    path('review/', include([
        path('create/', CreateReviewView, name='create_review'),
        path('show/<int:pk>/', ShowReviewsUserView.as_view(), name='show_user_reviews'),
        path('delete/<int:pk>/', DeleteReviewView.as_view(), name='delete_review')
    ])),
)
