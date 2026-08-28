from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Portal role", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Portal role", {"fields": ("role",)}),
    )
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("role",)
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
