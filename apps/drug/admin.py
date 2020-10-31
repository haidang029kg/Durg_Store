from django.contrib import admin

from apps.drug.models import Drug, Category, Pharmacy, WorkSpace, UserWorkSpace


# Register your models here.

class CustomUserWorkSpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_space', 'user')


class CustomPharmacyAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_space', 'name')


admin.site.register(Drug)
admin.site.register(Category)
admin.site.register(Pharmacy, CustomPharmacyAdmin)
admin.site.register(WorkSpace)
admin.site.register(UserWorkSpace, CustomUserWorkSpaceAdmin)
