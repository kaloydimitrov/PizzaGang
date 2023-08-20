from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('PizzaGang.main.urls')),
    path('', include('PizzaGang.admin.urls')),
    path('', include('PizzaGang.authapp.urls')),
    path('', include('PizzaGang.user.urls'))
]
