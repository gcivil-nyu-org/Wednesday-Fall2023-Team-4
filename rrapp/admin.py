from django.contrib import admin

# Register your models here.

from .models import User, Renter, Rentee, Listing

admin.site.register(User)
admin.site.register(Renter)
admin.site.register(Rentee)
admin.site.register(Listing)