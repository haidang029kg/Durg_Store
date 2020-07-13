from django.contrib import admin

from apps.drug.models import Drug, Category, Pharmacy

# Register your models here.


admin.site.register(Drug)
admin.site.register(Category)
admin.site.register(Pharmacy)
