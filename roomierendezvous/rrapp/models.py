from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime

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

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    birth_date = models.DateField
    verified = models.BooleanField
    first_name = models.CharField(max_length=100)
    last_name =  models.CharField(max_length=100)
    profile_picture_url = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class Renter(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,)

class Rentee(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,)

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now())
    # TODO enum
    status = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
    monthly_rent = models.IntegerField(default=1000)
    date_available_from = models.DateField(default=datetime.date.today())
    date_available_to = models.DateField(default=datetime.date.today() + datetime.timedelta(days=30))
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
    # TODO
    # address = models.addresses
    # amenities amenities
    number_of_bedrooms = models.IntegerField(default=1)
    number_of_bathrooms = models.IntegerField(default=1)
    furnished = models.BooleanField(default=True)
    utilities_included = models.BooleanField(default=True)
    # TODO
    # # preferences preferences
    def __str__(self):
        return self.title