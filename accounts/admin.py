from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_verified_seller', 'is_staff')
    list_filter = ('role', 'is_verified_seller', 'is_staff')
