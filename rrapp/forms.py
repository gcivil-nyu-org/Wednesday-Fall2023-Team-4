from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'profile_picture_url',
            'smokes',
            'has_pets',
            'smokes',
            'password1',
            'password2',
        ]


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'profile_picture_url',
            'smokes',
            'has_pets',
            'smokes',
            'bio',
        ]