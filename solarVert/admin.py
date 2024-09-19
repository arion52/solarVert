# solar_management/admin.py
from django.contrib import admin
from .models import PowerUsage
from .models import PowerData

admin.site.register(PowerUsage)

admin.site.register(PowerData)
