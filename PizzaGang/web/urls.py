from django.urls import path, include
from .views import HomeView, SignUpView, SignInView, SignOutView, MenuView, CreatePizzaView

urlpatterns = (
    path('', HomeView.as_view(), name='home'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-out/', SignOutView.as_view(), name='sign-out'),
    path('menu', MenuView.as_view(), name='menu'),
    path('pizza/', include([
        path('create/', CreatePizzaView.as_view(), name='pizza-create')
    ]))
)
