from django.contrib import admin

# Register your models here.
from app1.models import *

admin.site.register(Profile)
admin.site.register(WeatherData)