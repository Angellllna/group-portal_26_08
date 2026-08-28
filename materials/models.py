import re
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.urls import reverse

# Кастомна транслітерація для кирилиці
TRANSLIT_DICT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh',
    'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh',
    'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
    'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '', 'Ю': 'Yu', 'Я': 'Ya'
}

def custom_slugify(text):
    for cyr, lat in TRANSLIT_DICT.items():
        text = text.replace(cyr, lat)
    return slugify(text)


class MaterialCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug (URL)")
    description = models.TextField(blank=True, null=True, verbose_name="Опис категорії")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок відображення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Категорія матеріалів"
        verbose_name_plural = "Категорії матеріалів"
        ordering = ['position', 'title']

    def __str__(self):
        return self.title

    def clean(self):
        if not self.title or not self.title.strip():
            raise ValidationError({'title': "Назва категорії не може бути порожньою або складатися лише з пробілів."})

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = custom_slugify(self.title)
        self.full_clean()
        super().save(*args, **kwargs)


class Material(models.Model):
    TYPE_FILE = 'file'
    TYPE_IMAGE = 'image'
    TYPE_LINK = 'link'
    TYPE_YOUTUBE = 'youtube'

    MATERIAL_TYPES = [
        (TYPE_FILE, "Файл"),
        (TYPE_IMAGE, "Зображення"),
        (TYPE_LINK, "Зовнішнє посилання"),
        (TYPE_YOUTUBE, "YouTube-відео"),
    ]

    title = models.CharField(max_length=255, verbose_name="Назва матеріалу")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug (URL)")
    description = models.TextField(max_length=3000, blank=True, null=True, verbose_name="Опис матеріалу")
    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name="Категорія"
    )
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES,
        verbose_name="Тип матеріалу"
    )
    file = models.FileField(upload_to='materials/files/', blank=True, null=True, verbose_name="Файл")
    image = models.ImageField(upload_to='materials/images/', blank=True, null=True, verbose_name="Зображення")
    external_url = models.URLField(blank=True, null=True, verbose_name="Зовнішнє посилання")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube-посилання")
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name="Автор"
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубліковано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Навчальний матеріал"
        verbose_name_plural = "Навчальні матеріали"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('materials:material_detail', kwargs={'slug': self.slug})

    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None
        pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)'
        match = re.search(pattern, self.youtube_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    def clean(self):
        if not self.title or not self.title.strip():
            raise ValidationError({'title': "Назва не може бути порожньою або складатися лише з пробілів."})

        if not self.category:
            raise ValidationError({'category': "Матеріал повинен належати до категорії."})

        if self.material_type == self.TYPE_FILE and not self.file:
            raise ValidationError({'file': "Для типу 'Файл' обов'язково завантажте файл."})
        elif self.material_type == self.TYPE_IMAGE and not self.image:
            raise ValidationError({'image': "Для типу 'Зображення' обов'язково додайте зображення."})
        elif self.material_type == self.TYPE_LINK and not self.external_url:
            raise ValidationError({'external_url': "Для типу 'Зовнішнє посилання' обов'язково вкажіть URL."})
        elif self.material_type == self.TYPE_YOUTUBE:
            if not self.youtube_url:
                raise ValidationError({'youtube_url': "Для типу 'YouTube-відео' обов'язково вкажіть посилання."})
            pattern = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+'
            if not re.match(pattern, self.youtube_url):
                raise ValidationError({'youtube_url': "Вкажіть коректне YouTube-посилання (наприклад, https://www.youtube.com/watch?v=... або https://youtu.be/...)"})

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = custom_slugify(self.title)
        self.full_clean()
        super().save(*args, **kwargs)