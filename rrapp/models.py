import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)

from psycopg2.extras import NumericRange


from django.contrib.postgres.serializers import RangeSerializer
from django.db.migrations.writer import MigrationWriter

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager

MigrationWriter.register_serializer(NumericRange, RangeSerializer)


# Create your models here.
class UserRole(models.TextChoices):
    RENTER = "renter", _("Renter")
    RENTEE = "rentee", _("Rentee")


class PropertyType(models.TextChoices):
    INDEPENDENT_HOUSE = "independent_house", _("Independent house")
    APARTMENT = "apartment", _("Apartment")

class GenderType(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")
    ALL = "All", _("All")

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


class Status(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")


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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, date_joined=timezone.now())

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.email}_{instance.id}.{ext}'
    return os.path.join('profile_pictures', filename)


def user_id_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.email}_{instance.id}.{ext}'
    return os.path.join('id_pictures', filename)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    birth_date = models.DateField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(default="")  # Does it nullable?
    profile_picture = models.ImageField(
        upload_to=user_directory_path,
        height_field=None,
        width_field=None,
        null=True,
        blank=True,
    )
    id_picture = models.ImageField(
        upload_to=user_id_directory_path,
        height_field=None,
        width_field=None,
        blank=True,
        null=True,
    )
    smokes = models.BooleanField(default=False)
    pets = models.CharField(
        max_length=20,
        choices=Pets.choices,
        default=Pets.NONE,
    )
    food_group = models.CharField(
        max_length=20,
        choices=FoodGroup.choices,
        default=FoodGroup.ALL,
    )
    phone_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_student = models.BooleanField(default=False)
    rating = models.FloatField(null=True, default=None, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Renter(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="renter",
    )


class Rentee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rentee",
    )


class Quiz(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz",
    )
    question1 = models.IntegerField(
        choices=[
            (1, "In your roommate's bed"),
            (2, 'On the couch'),
            (3, 'In your bed'),
        ],
        null=True,
    )
    question2 = models.IntegerField(
        choices=[
            (
                1,
                "Wait for that paycheck – you'll just "
                "have to spend as little as possible until then.",
            ),
            (
                2,
                "Ask your roommate for a small loan and pay "
                "him/her back when you get your paycheck.",
            ),
            (
                3,
                "Ask your roommate for a small loan,"
                "and pay him/her back in installments.",
            ),
            (
                4,
                "Take some money out of your roommate's "
                "top drawer and return it as soon as you get your pay.",
            ),
        ],
        null=True,
    )
    question3 = models.IntegerField(
        choices=[
            (
                1,
                "Borrow the jacket and put it back before your "
                "roommate gets home – you'll only be gone for a few hours.",
            ),
            (
                2,
                "Borrow the jacket and explain to your "
                "roommate later how dire your situation was.",
            ),
            (
                3,
                "Try to get a hold of him/her" " and ask if you can borrow the jacket.",
            ),
            (4, "Find something else to wear to dinner."),
        ],
        null=True,
    )
    question4 = models.IntegerField(
        choices=[
            (
                1,
                "Go out looking for him/her so you can "
                "give him/her the message personally.",
            ),
            (
                2,
                "Write the note twice and put one on the "
                "bulletin board and the other in a place where she/he is sure to find it.",
            ),
            (3, "Leave him/her a note on the fridge."),
            (
                4,
                "Don't write the message but remind yourself"
                " to pass the message along when you see him/her.",
            ),
            (5, "Tell him/her when she/he gets home."),
        ],
        null=True,
    )
    question5 = models.IntegerField(
        choices=[
            (
                1,
                "Pick up the slack and take on some of your "
                "roommate's responsibilities yourself.",
            ),
            (
                2,
                "Nothing, just lower your living standards to keep in "
                "line with those of your roommate. Maybe she/he will get so "
                "sick of the mess that she/he will actually start cleaning up.",
            ),
            (
                3,
                "Mope around hoping she/he will ask you what's "
                "up and then complain about the state of the house.",
            ),
            (4, "Mention it once in a casual tone and hope she/he gets the message."),
            (5, "Have a serious talk with your roommate as soon as possible."),
            (
                6,
                "Tell him/her straight out that she/he has to do more around the"
                " place - there is no need to soften the demand with 'please' and 'thank you'.",
            ),
            (
                7,
                "Accuse him/her of being a lazy slob and threaten non-payment "
                "of the rent if she/he doesn't clean up her/his act - literally.",
            ),
        ],
        null=True,
    )
    question6 = models.IntegerField(
        choices=[
            (
                1,
                "Put the computer back where you found it and claim to have"
                " never touched it when your roommate asks about it.",
            ),
            (
                2,
                "Take it to the computer store and pay for the repairs but "
                "don't tell your roommate when s/he gets home.",
            ),
            (
                3,
                "Tell your roommate what happened when she/he gets back, "
                "hoping s/he won't ask you to pay for the damage.",
            ),
            (
                4,
                "Take it to the computer store and pay for the repairs, explaining "
                "the accident to your roommate when she/he gets home.",
            ),
            (
                5,
                "Wait for your roommate to get home, explain the situation, and "
                "offer to pay for the damage.",
            ),
            (
                6,
                "Contact your roommate prior to his/her arrival home and explain "
                "the situation. Ask her/him how to proceed, emphasizing "
                "that you'll do whatever it takes to fix the situation.",
            ),
        ],
        null=True,
    )
    question7 = models.IntegerField(
        choices=[
            (1, "Suggest an all-night café or club."),
            (2, "Call your roommate and ask if it is okay to have people over."),
            (
                3,
                "Invite them all over to your place but make "
                "them promise to keep the “fun” volume down.",
            ),
            (
                4,
                "Throw caution to the wind and invite everyone over"
                " - your roommate will survive a bit of noise.",
            ),
        ],
        null=True,
    )
    question8 = models.IntegerField(
        choices=[
            (1, "You'll pay the bill on time."),
            (2, "You'll forget at first, but end up paying it before the deadline."),
            (3, "You'll forget until your roommate reminds you."),
            (
                4,
                "You'll give the money to your roommate and let him/her take care of it.",
            ),
            (
                5,
                "You'll remember that the bill has to be paid, "
                "but end up procrastinating and paying it late.",
            ),
            (6, "You'll forget and end up paying it way passed the deadline."),
        ],
        null=True,
    )


class SavedListing(models.Model):
    rentee_id = models.ForeignKey(
        Rentee, related_name="saved_listing", on_delete=models.CASCADE, null=True
    )
    saved_listings = models.ForeignKey(
        "Listing", related_name="rentee", on_delete=models.CASCADE, null=True
    )


class Listing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=100,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
    monthly_rent = models.IntegerField(default=1000)
    date_available_from = models.DateField(default=timezone.now)
    date_available_to = models.DateField(default=timezone.now)
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
    gender_type = models.CharField(
        max_length=20,
        choices=GenderType.choices,
        default=GenderType.ALL,
    )
    address1 = models.CharField("Address line 1", max_length=1024, default="")

    address2 = models.CharField("Address line 2", max_length=1024, default="")

    zip_code = models.CharField("ZIP / Postal code", max_length=12, default="11201")

    city = models.CharField("City", max_length=100, default="New York")

    state = models.CharField("State", max_length=15, default="New York")

    country = models.CharField("Country", max_length=3, default="US")

    # utilities
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

    # preferences
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
    restrict_to_matches = models.BooleanField(default=False)


def get_uploaded_to(instance, filename):
    return 'listing_photos/{}/{}'.format(instance.listing.id, filename)


class Photo(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to=get_uploaded_to, blank=True, null=True)

    def __str__(self):
        return str(self.listing.title) + ": " + str(self.image)


class Rating(models.Model):
    rater = models.ForeignKey(
        "User",
        related_name="rater",
        on_delete=models.SET_NULL,
        null=True,
    )
    ratee = models.ForeignKey(
        "User",
        related_name="ratee",
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(null=True, default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
