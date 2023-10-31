from django.contrib import admin

# Register your models here.

from .models import User, Renter, Rentee, Listing
# from .models import User, Listing

admin.site.register(User)
admin.site.register(Renter)
admin.site.register(Rentee)
admin.site.register(Listing)
