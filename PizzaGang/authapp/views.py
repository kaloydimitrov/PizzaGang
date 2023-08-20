from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm, SignInForm


User = get_user_model()


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'authentication/sign_up.html'
    success_url = reverse_lazy('sign_in')


class SignInView(LoginView):
    form_class = SignInForm
    template_name = 'authentication/sign_in.html'
    next_page = reverse_lazy('home')


class SignOutView(LogoutView):
    next_page = reverse_lazy('home')
