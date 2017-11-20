from django.contrib import admin

# Register your models here.
from . import models
from .models import User,Message


admin.site.register(models.User)
admin.site.register(models.Message)