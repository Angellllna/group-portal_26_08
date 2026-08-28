from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse




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

   



    def __str__(self):
        return self.title

@property
def posts_count(self):
    return sum(thread.posts.count() for thread in self.threads.all())



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

    def get_absolute_url(self):
        return reverse("forum:thread_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Гілка"
        verbose_name_plural = "Гілки"

    

    def clean(self):
        if self.category and not self.category.is_active:
            raise ValidationError({'category': "Неможливо створити гілку в неактивній категорії."})


    def __str__(self):
        return self.title


class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, related_name="posts", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()  # ← ось цього поля не вистачає
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()


    class Meta:
        ordering = ['created_at']
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

   


    def __str__(self):
        return f"Повідомлення від {self.author} у {self.thread.title}"
    
