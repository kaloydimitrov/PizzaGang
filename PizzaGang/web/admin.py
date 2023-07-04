from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Pizza
from .forms import SignUpForm, MyUserChangeForm


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = SignUpForm

    list_display = ('email', 'first_name', 'last_name', 'username', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'date_of_birth', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, MyUserAdmin)
admin.site.register(Pizza)
