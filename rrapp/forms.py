from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
import datetime

from .models import PropertyType, RoomType, Pets, FoodGroup, Listing
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(),
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if '@' not in email:
            raise forms.ValidationError("Please enter a valid email")
        elif not User.objects.filter(email=email).exists():
            raise forms.ValidationError("The user corresponding to the email does not exist")
        elif not email.endswith(".edu"):
            raise forms.ValidationError("Please enter a valid school email. End with .edu")
        return email
        

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "profile_picture",
            "smokes",
            "pets",
            "food_group",
            "password1",
            "password2",
        ]
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if len(first_name) == 0:
            raise forms.ValidationError("Please enter a first name")
        elif len(first_name) > 30:
            raise forms.ValidationError("First name is too long")
        elif not first_name.isalpha():
            raise forms.ValidationError("First name must only contain letters")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if len(last_name) == 0:
            raise forms.ValidationError("Please enter a last name")
        elif len(last_name) > 30:
            raise forms.ValidationError("Last name is too long")
        elif not last_name.isalpha():
            raise forms.ValidationError("Last name must only contain letters")
        return last_name
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) == 0:
            raise forms.ValidationError("Please enter a username")
        elif len(username) > 30:
            raise forms.ValidationError("Username is too long")
        elif not username.isalnum():
            raise forms.ValidationError("Username must only contain letters and numbers")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if len(email) == 0:
            raise forms.ValidationError("Please enter an email")
        elif '@' not in email:
            raise forms.ValidationError("Please enter a valid email")
        elif len(email) > 100:
            raise forms.ValidationError("Email is too long")
        elif not email.endswith(".edu"):
            raise forms.ValidationError("Please enter a valid school email. End with .edu")
        elif User.objects.filter(email=email).exists():
            raise forms.ValidationError("The email is already in use")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if len(phone_number) == 0:
            raise forms.ValidationError("Please enter a phone number")
        elif len(phone_number) > 15:
            raise forms.ValidationError("Please enter a valid phone number")
        elif not phone_number.isdigit():
            raise forms.ValidationError("Phone number must only contain numbers")
        return phone_number
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) == 0:
            raise forms.ValidationError("Please enter a password")
        elif len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        elif not any(char.isdigit() for char in password1):
            raise forms.ValidationError("Password must contain at least one number")
        elif not any(char.isalpha() for char in password1):
            raise forms.ValidationError("Password must contain at least one letter")
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if len(password2) == 0:
            raise forms.ValidationError("Please enter password again")
        elif password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

class UserForm(ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "bio",
            "smokes",
            "pets",
            "food_group",
            "phone_number",
            "profile_picture",
        ]
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) == 0:
            raise forms.ValidationError("Please enter a username")
        elif len(username) > 30:
            raise forms.ValidationError("Username is too long")
        elif not username.isalnum():
            raise forms.ValidationError("Username must only contain letters and numbers")
        return username
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if len(first_name) == 0:
            raise forms.ValidationError("Please enter a first name")
        elif len(first_name) > 30:
            raise forms.ValidationError("First name is too long")
        elif not first_name.isalpha():
            raise forms.ValidationError("First name must only contain letters")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if len(last_name) == 0:
            raise forms.ValidationError("Please enter a last name")
        elif len(last_name) > 30:
            raise forms.ValidationError("Last name is too long")
        elif not last_name.isalpha():
            raise forms.ValidationError("Last name must only contain letters")
        return last_name
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if len(phone_number) == 0:
            raise forms.ValidationError("Please enter a phone number")
        elif len(phone_number) > 15:
            raise forms.ValidationError("Please enter a valid phone number")
        elif not phone_number.isdigit():
            raise forms.ValidationError("Phone number must only contain numbers")
        return phone_number
    
    def clean_bio(self):
        bio = self.cleaned_data.get("bio")
        if len(bio) > 500:
            raise forms.ValidationError("Bio is too long")
        return bio

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if birth_date > datetime.date.today():
            raise forms.ValidationError("Birth date cannot be in the future")
        return birth_date

class ListingForm(ModelForm):
    date_available_from = forms.DateField(
        initial=datetime.date.today(),
        widget=forms.DateInput(attrs={'type': 'date'}))
    date_available_to = forms.DateField(
        initial=datetime.date.today() + datetime.timedelta(days=30),
        widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Listing
        fields = [
            "status",
            "title",
            "description",
            "monthly_rent",
            "date_available_from",
            "date_available_to",
            "property_type",
            "room_type",
            "address1",
            "address2",
            "zip_code",
            "city",
            "state",
            "country",
            "washer",
            "dryer",
            "dishwasher",
            "microwave",
            "baking_oven",
            "parking",
            "number_of_bedrooms",
            "number_of_bathrooms",
            "furnished",
            "utilities_included",
            "age_range",
            "smoking_allowed",
            "pets_allowed",
            "food_groups_allowed",
        ]

    def clean_monthly_rent(self):
        monthly_rent = self.cleaned_data.get("monthly_rent")
        if monthly_rent < 0:
            raise forms.ValidationError("Monthly rent cannot be negative")
        return monthly_rent
    
    def clean_date_available_from(self):
        date_available_from = self.cleaned_data.get("date_available_from")
        if date_available_from < datetime.date.today():
            raise forms.ValidationError("Date available from cannot be in the past")
        return date_available_from
    
    def clean_date_available_to(self):
        date_available_to = self.cleaned_data.get("date_available_to")
        if date_available_to < datetime.date.today():
            raise forms.ValidationError("Date available to cannot be in the past")
        elif date_available_to < self.date_available_from():
            raise forms.ValidationError("Date available to cannot be before date available from")
        return date_available_to
    
    def clean_number_of_bedrooms(self):
        number_of_bedrooms = self.cleaned_data.get("number_of_bedrooms")
        if number_of_bedrooms < 0:
            raise forms.ValidationError("Number of bedrooms cannot be negative")
        return number_of_bedrooms
    
    def clean_number_of_bathrooms(self):
        number_of_bathrooms = self.cleaned_data.get("number_of_bathrooms")
        if number_of_bathrooms < 0:
            raise forms.ValidationError("Number of bathrooms cannot be negative")
        return number_of_bathrooms
    
    def clean_age_range(self):
        age_range = self.cleaned_data.get("age_range")
        if age_range.lower < 18:
            raise forms.ValidationError("Minimum age cannot be less than 18")
        elif age_range.upper > 100:
            raise forms.ValidationError("Maximum age cannot be greater than 100")
        return age_range
    