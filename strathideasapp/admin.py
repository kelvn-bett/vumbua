from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Ideas, Comments, Industry_category, Roles

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'category', 'phone_number', 'role', 'has_voted']


class IdeasAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'date_posted', 'category', 'approved', 'denied', 'total']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Ideas, IdeasAdmin)
admin.site.register(Comments)
admin.site.register(Industry_category)
admin.site.register(Roles)


admin.site.site_header = 'Vumbua Administration'
