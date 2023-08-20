from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DeleteView
from .forms import UserEditForm, ProfileEditForm, ReviewForm
from PizzaGang.main.models import Profile, Order, Review


User = get_user_model()


class UserShowPublicView(View):
    @staticmethod
    def get(request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return redirect(f'/user-info/show/{pk}/')

        review_list = Review.objects.filter(user=user)

        context = {
            'review_list': review_list,
            'user': user
        }

        return render(request, 'user_info/show_public_info.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class UserShowView(View):
    @staticmethod
    def get(request, pk):
        if request.user.pk != pk:
            return redirect(f'/user-info/show/{request.user.pk}/')

        user = get_object_or_404(User, pk=pk)

        context = {
            'user': user
        }

        return render(request, 'user_info/show_info.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class UserAddressView(TemplateView):
    template_name = 'user_info/show_address.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class ShowOrdersUserView(ListView):
    model = Order
    template_name = 'orders/show_user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return Order.objects.filter(user=user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.request.user.pk)
        active_orders_count = Order.objects.filter(user=user, is_finished=False).count()
        context['active_orders_count'] = active_orders_count
        return context


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class DeleteOrderView(DeleteView):
    model = Order
    success_url = reverse_lazy('menu')


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class ShowReviewsUserView(ListView):
    template_name = 'review/show_user_reviews.html'
    context_object_name = 'review_list'

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return Review.objects.filter(user=user).order_by('-created_at')


@login_required(login_url=reverse_lazy('sign_in'))
def CreateReviewView(request):
    user = request.user

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        rating = request.POST.get('rating')
        if form.is_valid():
            review = Review(user=user, rating=rating, text=form.cleaned_data['text'])
            review.save()

            return redirect(f'/review/show/{user.pk}/')
    else:
        form = ReviewForm()

    context = {
        'form': form
    }

    return render(request, 'review/create_review.html', context)


@method_decorator(login_required(login_url=reverse_lazy('sign_in')), name='dispatch')
class DeleteReviewView(DeleteView):
    model = Review
    template_name = 'review/show_user_reviews.html'

    def get_success_url(self):
        user_pk = self.request.user.pk
        return reverse('show_user_reviews', kwargs={'pk': user_pk})


@login_required(login_url=reverse_lazy('sign_in'))
def UserEditView(request, pk):
    if request.user.pk != pk:
        return redirect('home')

    user = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(f'/user-info/show/{pk}/')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user
    }

    return render(request, 'user_info/edit_info.html', context)
