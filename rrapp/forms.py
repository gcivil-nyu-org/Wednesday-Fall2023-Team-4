from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta:
#        model = Renter
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'profile_picture_url', 'smokes', 'has_pets', 'smokes', 'password1', 'password2']


# class RoomForm(ModelForm):
#     class Meta:
#         model = Room
#         fields = '__all__'
#         exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'profile_picture_url', 'smokes', 'has_pets', 'smokes', 'bio']