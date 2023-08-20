from django import forms
from PizzaGang.main.models import Profile, Review
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text', )
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Enter your thoughts...'})
        }
