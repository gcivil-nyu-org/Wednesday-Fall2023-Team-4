from django.contrib import admin
from .models import DirectMessage, DirectMessagePermission


# Register your models here.
admin.site.register(DirectMessage)
admin.site.register(DirectMessagePermission)
