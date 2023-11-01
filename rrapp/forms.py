from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
import datetime

from .models import User, PropertyType, RoomType, Pets, FoodGroup, Listing
from django.contrib.auth import get_user_model

User = get_user_model()


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


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'status',
            'title',
            'description',
            'monthly_rent',
            'date_available_from',
            'date_available_to',
            'property_type',
            'room_type',
            'address1',
            'address2',
            'zip_code',
            'city',
            'country',
            'washer',
            'dryer',
            'dishwasher',
            'microwave',
            'baking_oven',
            'parking',
            'number_of_bedrooms',
            'number_of_bathrooms',
            'furnished',
            'utilities_included',
            'age_range',
            'smoking_allowed',
            'pets_allowed',
            'food_groups_allowed',
        ]

    status = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter status"}
        ),
    )
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter title"}
        ),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Enter useful description"}
        ),
    )
    monthly_rent = forms.IntegerField(
        label="monthly_rent",
        initial=1001,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter monthly rent"}
        ),
    )
    date_available_from = forms.DateField(
        label="date_available_from",
        initial=datetime.date.today(),
        widget=forms.DateInput(
            attrs={"class": "form-control", "placeholder": "Enter date available from"}
        ),
    )
    date_available_to = forms.DateField(
        label="date_available_to",
        initial=datetime.date.today() + datetime.timedelta(days=30),
        widget=forms.DateInput(
            attrs={"class": "form-control", "placeholder": "Enter date available to"}
        ),
    )
    property_type = forms.ChoiceField(
        label="property_type",
        choices=PropertyType.choices,
        initial=PropertyType.APARTMENT,
    )
    room_type = forms.ChoiceField(
        label="room_type",
        choices=RoomType.choices,
        initial=RoomType.PRIVATE,
    )
    address1 = forms.CharField(
        label="Address line 1",
        max_length=1024,
        initial="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter address line 1"}
        ),
    )

    address2 = forms.CharField(
        label="Address line 2",
        max_length=1024,
        initial="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter address line 2"}
        ),
    )

    zip_code = forms.CharField(
        label="ZIP / Postal code",
        max_length=12,
        initial="11201",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter zipcode"}
        ),
    )

    city = forms.CharField(
        label="City",
        max_length=1024,
        initial="New York",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter city"}
        ),
    )

    country = forms.CharField(
        label="Country",
        max_length=3,
        initial="USA",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter country"}
        ),
    )

    # # TODO: can we use a nested field?
    washer = forms.BooleanField(
        label="washer",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    dryer = forms.BooleanField(
        label="dryer",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    dishwasher = forms.BooleanField(
        label="dishwasher",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    microwave = forms.BooleanField(
        label="microwave",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    baking_oven = forms.BooleanField(
        label="baking_oven",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    parking = forms.BooleanField(
        label="parking",
        initial=False,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )

    number_of_bedrooms = forms.IntegerField(
        label="number_of_bedrooms",
        initial=1,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter monthly rent"}
        ),
    )
    number_of_bathrooms = forms.IntegerField(
        label="number_of_bathrooms",
        initial=1,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter monthly rent"}
        ),
    )
    furnished = forms.BooleanField(
        label="furnished",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    utilities_included = forms.BooleanField(
        label="utilities_included",
        initial=True,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    # TODO : can we use a nested field? like preferences = Preference(label = "
    # TODO : can we use a nested field? like preferences", )
    # age_range_0 = forms.IntegerField(label = "age_range_0",
    #     initial=18,
    #     required=False,
    #     widget=forms.NumberInput(
    #         attrs={"class": "form-control", "placeholder": "Enter minimum age"}
    #     )
    # )
    # age_range_1 = forms.IntegerField(label = "age_range_1",
    #     initial=99,
    #     required=False,
    #     widget=forms.NumberInput(
    #         attrs={"class": "form-control", "placeholder": "Enter maximum age"}
    #     )
    # )
    smoking_allowed = forms.BooleanField(
        label="smoking_allowed",
        initial=False,
        required=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "form-control", "placeholder": "Select availability"}
        ),
    )
    pets_allowed = forms.ChoiceField(
        label="pets_allowed",
        choices=Pets.choices,
        initial=Pets.NONE,
    )
    food_groups_allowed = forms.ChoiceField(
        label="food_groups_allowed",
        choices=FoodGroup.choices,
        initial=FoodGroup.ALL,
    )
