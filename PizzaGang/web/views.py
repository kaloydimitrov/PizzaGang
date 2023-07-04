from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from .forms import SignUpForm, CreatePizzaForm


def BaseView(request):
    context = {
        'user': request.user
    }

    return render(request, 'base/base.html', context)


class HomeView(TemplateView):
    template_name = 'index.html'


class SignUpView(CreateView):
    template_name = 'sign_up.html'
    form_class = SignUpForm
    success_url = reverse_lazy('sign-in')


class SignInView(LoginView):
    template_name = 'sign_in.html'
    next_page = reverse_lazy('home')


class SignOutView(LogoutView):
    next_page = reverse_lazy('home')


class MenuView(TemplateView):
    template_name = 'menu.html'


class CreatePizzaView(CreateView):
    template_name = 'create_pizza.html'
    form_class = CreatePizzaForm
