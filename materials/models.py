from django.db import models
from django.contrib.auth.models import User


class Material(models.Model):
    CATEGORY_CHOICES = [
        ("masking", "Основи маскування"),
        ("planning", "Планування операцій"),
        ("teamwork", "Командна робота"),
        ("security", "Обхід систем безпеки"),
        ("codes", "Шифри та коди"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="materials"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to="materials/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title