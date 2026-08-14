from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Material(models.Model):
    class Category(models.TextChoices):
        MASKING = "masking", "Основи маскування"
        PLANNING = "planning", "Планування операцій"
        TEAMWORK = "teamwork", "Командна робота"
        SECURITY = "security", "Обхід систем безпеки"
        CODES = "codes", "Шифри та коди"

    class MaterialType(models.TextChoices):
        FILE = "file", "Файл"
        IMAGE = "image", "Зображення"
        LINK = "link", "Посилання"
        YOUTUBE = "youtube", "YouTube"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="materials"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
        default=MaterialType.FILE,
    )
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        # allow_unicode=True — інакше кирилиця перетворюється на порожній рядок
        base = slugify(self.title, allow_unicode=True) or "material"
        slug = base
        counter = 2
        while Material.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

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

    @property
    def file_name(self):
        """Ім'я файлу без теки, для показу користувачу."""
        if not self.file:
            return ""
        return self.file.name.rsplit("/", 1)[-1]

    @property
    def file_extension(self):
        """Розширення файлу у верхньому регістрі, наприклад PDF."""
        name = self.file_name
        if "." not in name:
            return ""
        return name.rsplit(".", 1)[-1].upper()

    @property
    def youtube_embed_url(self):
        """Безпечна адреса для вбудовування — будується з ID, а не з сирого посилання."""
        if not self.link:
            return None

        parsed = urlparse(self.link)

        # https://www.youtube.com/watch?v=...
        if parsed.hostname in ("www.youtube.com", "youtube.com"):
            video_id = parse_qs(parsed.query).get("v")

            if video_id:
                return f"https://www.youtube.com/embed/{video_id[0]}"

        # https://youtu.be/...
        if parsed.hostname == "youtu.be":
            video_id = parsed.path.lstrip("/")

            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        return None
