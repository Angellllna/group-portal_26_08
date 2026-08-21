from django.contrib import admin
from .models import ForumCategory, ForumThread, ForumPost

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'position', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('position',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_pinned', 'is_closed', 'created_at')
    list_filter = ('is_pinned', 'is_closed', 'category', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    ordering = ('-is_pinned', '-created_at')


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'thread__title')
    ordering = ('created_at',)