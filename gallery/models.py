from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

# Create your models here.

class MediaType(models.TextChoices):
    IMAGE = "image", "Фото"
    VIDEO = "video", "Відео"

class Status(models.TextChoices):
    PENDING = "pending", "Очікує перевірки"
    APPROVED = "approved", "Схвалено"
    REJECTED = "rejected", "Відхилено"


class PENDING:
    """Concrete helper for the pending moderation state."""

    @staticmethod
    def value():
        return Status.PENDING

    @staticmethod
    def label():
        return Status.PENDING.label

    @staticmethod
    def is_pending(value):
        return value == Status.PENDING or value == Status.PENDING.value

    @staticmethod
    def next_status():
        return Status.APPROVED


class GalleryItemQuerySet(models.QuerySet):
    def search(self, query):
        if not query:
            return self

        return self.filter(
            Q(title__icontains=query)
            | Q(author__username__icontains=query)
            | Q(author__first_name__icontains=query)
            | Q(author__last_name__icontains=query)
        ).distinct()

    def filter_by(self, media_type=None, status=None, date_from=None, date_to=None):
        filters = {}
        if media_type:
            filters["media_type"] = media_type
        if status:
            filters["status"] = status
        if date_from:
            filters["created_at__date__gte"] = date_from
        if date_to:
            filters["created_at__date__lte"] = date_to
        return self.filter(**filters)


class GalleryItem(models.Model):
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm"}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    MAX_VIDEO_SIZE = 100 * 1024 * 1024

    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
    upload_to = "gallery/images/", blank=True, null=True)
    video = models.FileField(upload_to="gallery/videos/", blank=True, null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    media_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')], default='image')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gallery_items')
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    moderation_comment = models.TextField(blank=True, null=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_gallery_items')
    updated_at = models.DateTimeField(auto_now=True)
    moderated_at = models.DateTimeField(null=True, blank=True)

    objects = GalleryItemQuerySet.as_manager()

    class Meta:
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"
        ordering = ['-created_at']

    def clean(self):
        errors = {}

        if self.media_type == MediaType.IMAGE and not self.image:
            errors["image"] = "Зображення є обов'язковим для типу «Фото»."
        elif self.media_type == MediaType.VIDEO and not self.video:
            errors["video"] = "Відео є обов'язковим для типу «Відео»."

        if self.image and self.image.name.rsplit(".", 1)[-1].lower() not in self.ALLOWED_IMAGE_EXTENSIONS:
            errors["image"] = "Дозволені формати зображень: JPG, JPEG, PNG та WEBP."

        if self.video and self.video.name.rsplit(".", 1)[-1].lower() not in self.ALLOWED_VIDEO_EXTENSIONS:
            errors["video"] = "Дозволені формати відео: MP4 та WEBM."

        if self.image and self.image.size > self.MAX_IMAGE_SIZE:
            errors["image"] = "Розмір зображення не може перевищувати 10 МБ."

        if self.video and self.video.size > self.MAX_VIDEO_SIZE:
            errors["video"] = "Розмір відео не може перевищувати 100 МБ."

        if self.media_type not in MediaType.values:
            errors["media_type"] = "Оберіть коректний тип медіа."

        if self.status not in {"draft", "published", *Status.values}:
            errors["status"] = "Оберіть коректний статус."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"



