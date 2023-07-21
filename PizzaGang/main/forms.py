from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Pizza, Offer
from django.utils.translation import gettext_lazy as _


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None
        self.fields['email'].help_text = None


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Name',
            'last_name': 'Surname',
            'email': 'Email'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = None
        self.fields['first_name'].help_text = None
        self.fields['last_name'].help_text = None
        self.fields['email'].help_text = None


class ProfileEditForm(forms.ModelForm):
    address = forms.CharField(max_length=100, required=False)
    avatar = forms.ImageField(label=_('avatar'), required=False, error_messages={'invalid': _("Image files only")},
                              widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ('avatar', 'address', 'phone_number')


class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizza
        fields = '__all__'


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('final_price', 'name', 'image', 'is_active')
