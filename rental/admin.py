#from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Property, Tenant, RentRecord

admin.site.register(Property)
admin.site.register(Tenant)
admin.site.register(RentRecord)
