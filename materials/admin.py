from django.contrib import admin
from .models import Material, MaterialCategory


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('position', 'title')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'material_type', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'material_type', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')