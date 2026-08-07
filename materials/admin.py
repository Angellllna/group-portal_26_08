from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "material_type",
        "author",
        "created_at",
        "is_published",
    )

    list_filter = (
        "category",
        "material_type",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
        "author__username",
    )

    ordering = (
        "-created_at",
    )