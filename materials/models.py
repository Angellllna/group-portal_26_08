from django.db import models
from django.contrib.auth.models import User
from urllib.parse import urlparse, parse_qs


class Material(models.Model):
    CATEGORY_CHOICES = [
        ("masking", "Основи маскування"),
        ("planning", "Планування операцій"),
        ("teamwork", "Командна робота"),
        ("security", "Обхід систем безпеки"),
        ("codes", "Шифри та коди"),
    ]

    TYPE_CHOICES = [
        ("file", "Файл"),
        ("image", "Зображення"),
        ("link", "Посилання"),
        ("youtube", "YouTube"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="materials",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
    )

    material_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="file",
    )

    file = models.FileField(
        upload_to="materials/",
        blank=True,
        null=True,
    )

    link = models.URLField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def youtube_embed_url(self):
        if not self.link:
            return None

        parsed = urlparse(self.link)

        if parsed.hostname in ("www.youtube.com", "youtube.com"):
            video_id = parse_qs(parsed.query).get("v")
            if video_id:
                return f"https://www.youtube.com/embed/{video_id[0]}"

        if parsed.hostname == "youtu.be":
            video_id = parsed.path.lstrip("/")
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        return None