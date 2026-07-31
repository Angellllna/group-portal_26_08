from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "codename")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "codename")
    ordering = ("user__username",)
