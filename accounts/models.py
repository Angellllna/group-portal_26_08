from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "Користувач"
        MODERATOR = "moderator", "Модератор"
        ADMIN = "admin", "Адміністратор"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def is_moderator_role(self):
        return self.role == self.Role.MODERATOR

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    def can_moderate(self):
        return self.is_moderator_role() or self.is_admin_role()

    def __str__(self):
        return self.username
