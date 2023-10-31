from django.contrib import admin

# Register your models here.

from .models import User, Renter, Rentee, Listing, SavedListing

admin.site.register(User)
admin.site.register(Renter)
admin.site.register(Rentee)
admin.site.register(Listing)
admin.site.register(SavedListing)
