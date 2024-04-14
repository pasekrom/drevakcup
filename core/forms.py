from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User  # Import your custom user model


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'name')  # Include any additional fields you want in the form


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'name', 'first_name', 'last_name', 'is_active', 'is_staff')  # Include any additional fields you want in the form
