from django.contrib import admin
from .models import Order, Produce

admin.site.register(Produce)
admin.site.register(Order)
