from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(PizzaCat)
admin.site.register(Pizza)
admin.site.register(Cart)
admin.site.register(CartItems)