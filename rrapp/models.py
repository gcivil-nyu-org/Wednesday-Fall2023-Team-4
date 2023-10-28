from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime

from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)

from psycopg2.extras import NumericRange


from django.contrib.postgres.serializers import RangeSerializer
from django.db.migrations.writer import MigrationWriter

MigrationWriter.register_serializer(NumericRange, RangeSerializer)


# Create your models here.
class UserRole(models.TextChoices):
    RENTER = "renter", _("Renter")
    RENTEE = "rentee", _("Rentee")


class PropertyType(models.TextChoices):
    INDEPENDENT_HOUSE = "independent_house", _("Independent house")
    APARTMENT = "apartment", _("Apartment")


class RoomType(models.TextChoices):
    PRIVATE = "private", _("Private")
    SHARED = "shared", _("Shared")


class FoodGroup(models.TextChoices):
    VEGAN = "vegan", _("Vegan")
    VEGETARIAN = "vegetarian", _("Vegetarian")
    NON_VEGETARIAN = "non_vegetarian", _("Non Vegetarian")
    ALL = "all", _("All")


class Pets(models.TextChoices):
    CATS = "cats", _("Cats")
    DOGS = "dogs", _("Dogs")
    NONE = "none", _("None")
    ALL = "all", _("All")


# class Address(models.Model):
#     line1 = models.CharField(max_length=100)
#     line2 = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     country = models.CharField(max_length=100)
#     zipcode = models.CharField(max_length=10)


class Preference(models.Model):
    age_range = IntegerRangeField(
        default=NumericRange(1, 101),
        blank=True,
        validators=[RangeMinValueValidator(1), RangeMaxValueValidator(100)],
    )
    smoking_allowed = models.BooleanField()
    pets_allowed = models.CharField(
        max_length=20,
        choices=Pets.choices,
        default=Pets.NONE,
    )
    food_groups_allowed = models.CharField(
        max_length=20,
        choices=FoodGroup.choices,
        default=FoodGroup.ALL,
    )


class Amenities(models.Model):
    washer = models.BooleanField(default=True)
    dryer = models.BooleanField(default=True)
    dishwasher = models.BooleanField(default=True)
    microwave = models.BooleanField(default=True)
    baking_oven = models.BooleanField(default=True)
    parking = models.BooleanField(default=False)


class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    # birth_date = models.DateField(default=datetime.date.today())
    # verified = models.BooleanField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture_url = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)


class Renter(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class Rentee(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    # TODO enum
    status = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
    monthly_rent = models.IntegerField(default=1000)
    date_available_from = models.DateField(default=timezone.now)
    date_available_to = models.DateField(
        default=timezone.now
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
    )
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.PRIVATE,
    )
    # TODO : can we use nested address field?
    address1 = models.CharField("Address line 1", max_length=1024, default="")

    address2 = models.CharField("Address line 2", max_length=1024, default="")

    zip_code = models.CharField("ZIP / Postal code", max_length=12, default="11201")

    city = models.CharField("City", max_length=1024, default="New York")

    country = models.CharField("Country", max_length=3, default="USA")

    # TODO: can we use a nested field?
    washer = models.BooleanField(default=True)
    dryer = models.BooleanField(default=True)
    dishwasher = models.BooleanField(default=True)
    microwave = models.BooleanField(default=True)
    baking_oven = models.BooleanField(default=True)
    parking = models.BooleanField(default=False)

    number_of_bedrooms = models.IntegerField(default=1)
    number_of_bathrooms = models.IntegerField(default=1)
    furnished = models.BooleanField(default=True)
    utilities_included = models.BooleanField(default=True)
    # TODO : can we use a nested field? like preferences = Preference()
    age_range = IntegerRangeField(
        default=NumericRange(18, 60),
        blank=True,
        validators=[RangeMinValueValidator(18), RangeMaxValueValidator(100)],
    )
    smoking_allowed = models.BooleanField(default=False)
    pets_allowed = models.CharField(
        max_length=20,
        choices=Pets.choices,
        default=Pets.NONE,
    )
    food_groups_allowed = models.CharField(
        max_length=20,
        choices=FoodGroup.choices,
        default=FoodGroup.ALL,
    )
