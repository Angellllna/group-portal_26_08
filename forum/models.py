from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_not_blank(value):
    """Проверка: строка не должна состоять только из пробелов."""
    if value and not value.strip():
        raise ValidationError("Це поле не може складатися лише з пробілів.")


class ForumCategory(models.Model):
    title = models.CharField(max_length=150, validators=[validate_not_blank], verbose_name="Назва")
    slug = models.SlugField(unique=True, verbose_name="URL-слаг")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок відображення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        ordering = ['position']
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def clean(self):
        super().clean()
        if self.title and not self.title.strip():
            raise ValidationError({'title': "Назва категорії не може складатися лише з пробілів."})

    def __str__(self):
        return self.title


class ForumThread(models.Model):
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name='threads',
        verbose_name="Категорія"
    )
    title = models.CharField(max_length=255, validators=[validate_not_blank], verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Опис")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_threads',
        verbose_name="Автор"
    )
    is_pinned = models.BooleanField(default=False, verbose_name="Закріплена")
    is_closed = models.BooleanField(default=False, verbose_name="Закрита")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Гілка"
        verbose_name_plural = "Гілки"

    def clean(self):
        super().clean()
        if self.title is not None and len(self.title.strip()) == 0:
            raise ValidationError({'title': "Назва гілки не може бути порожньою."})
        
        # Проверка: неактивная категория не должна использоваться при создании ветки
        if self.category_id and not self.category.is_active:
            raise ValidationError({'category': "Неможливо створити гілку в неактивній категорії."})

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Гілка"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_posts',
        verbose_name="Автор"
    )
    text = models.TextField(max_length=5000, validators=[validate_not_blank], verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

    def clean(self):
        super().clean()
        if self.text and not self.text.strip():
            raise ValidationError({'text': "Текст повідомлення не може складатися лише з пробілів."})

    def __str__(self):
        return f"Повідомлення від {self.author} у {self.thread.title}"
    
