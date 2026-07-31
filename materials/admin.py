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
    )
    search_fields = (
        "title",
        "description",
    )