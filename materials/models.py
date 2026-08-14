from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Material(models.Model):
    class Category(models.TextChoices):
        MASKING = "masking", "Основи маскування"
        PLANNING = "planning", "Планування операцій"
        TEAMWORK = "teamwork", "Командна робота"
        SECURITY = "security", "Обхід систем безпеки"
        CODES = "codes", "Шифри та коди"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="materials"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    file = models.FileField(upload_to="materials/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Матеріал"
        verbose_name_plural = "Матеріали"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if not self.title.strip():
            raise ValidationError({"title": "Назва не може бути порожньою."})
        if not self.description.strip():
            raise ValidationError({"description": "Опис не може бути порожнім."})
        # матеріал без файлу і без посилання не має сенсу
        if not self.file and not self.link:
            raise ValidationError(
                "Додайте файл або посилання — матеріал не може бути порожнім."
            )
