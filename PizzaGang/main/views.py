from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .forms import SignUpForm, UserEditForm, PizzaForm
from .models import Pizza


def BaseView(request):
    context = {
        'user': request.user
    }

    return render(request, 'base/base.html', context)


class HomeView(TemplateView):
    template_name = 'index.html'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'sign_up.html'
    success_url = reverse_lazy('sign_in')


class SignInView(LoginView):
    template_name = 'sign_in.html'
    next_page = reverse_lazy('home')


class SignOutView(LogoutView):
    next_page = reverse_lazy('home')


def UserEditView(request, pk):
    user = User.objects.get(pk=pk)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserEditForm(instance=user)

    context = {
        'form': form,
        'user': user
    }

    return render(request, 'user_info/edit_info.html', context)


def UserAddressView(request, pk):
    pass


class MenuView(ListView):
    template_name = 'pizza/menu.html'
    model = Pizza


def CreatePizzaView(request):
    if request.method == 'POST':
        form = PizzaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PizzaForm

    context = {
        'form': form,
    }

    return render(request, 'pizza/create_pizza.html', context)


class EditPizzaView(UpdateView):
    form_class = PizzaForm
    model = Pizza
    template_name = 'pizza/edit_pizza.html'
    success_url = reverse_lazy('home')


class DeletePizzaView(DeleteView):
    model = Pizza
    template_name = 'pizza/delete_pizza.html'
    success_url = reverse_lazy('home')
