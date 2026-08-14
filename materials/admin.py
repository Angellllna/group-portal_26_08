from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "created_at",
        "is_published",
    )
    list_filter = (
        "category",
        "is_published",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "author__username",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
