from django.contrib import admin

# Register your models here.

from .models import Renter, Rentee, Listing, SavedListing
from django.contrib.auth import get_user_model

User = get_user_model()

# from .models import User, Listing

admin.site.register(User)
admin.site.register(Renter)
admin.site.register(Rentee)
admin.site.register(Listing)
admin.site.register(SavedListing)
