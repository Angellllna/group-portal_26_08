from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Material


class MaterialModelTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="author01",
            email="author01@example.com",
            password="strong-password-123",
        )

    def _material(self, **kwargs):
        data = {
            "author": self.author,
            "title": "Основи маскування",
            "description": "Короткий конспект заняття",
            "category": Material.Category.MASKING,
            "material_type": Material.MaterialType.LINK,
            "link": "https://example.com/material",
        }
        data.update(kwargs)
        return Material(**data)

    def test_material_is_created_with_expected_fields(self):
        material = self._material()
        material.full_clean()
        material.save()

        self.assertEqual(material.author, self.author)
        self.assertEqual(material.category, "masking")
        self.assertTrue(material.is_published)

    def test_author_is_linked_to_project_user_model(self):
        material = self._material()
        material.save()

        self.assertEqual(
            Material._meta.get_field("author").remote_field.model,
            get_user_model(),
        )
        self.assertEqual(list(self.author.materials.all()), [material])

    def test_slug_is_built_from_cyrillic_title(self):
        material = self._material()
        material.save()

        self.assertEqual(material.slug, "основи-маскування")

    def test_duplicate_titles_get_unique_slugs(self):
        first = self._material()
        first.save()
        second = self._material()
        second.save()

        self.assertEqual(second.slug, "основи-маскування-2")

    def test_material_without_file_and_link_is_rejected(self):
        material = self._material(link="")

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_unknown_category_is_rejected(self):
        material = self._material(category="unknown")

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_file_name_and_extension(self):
        material = self._material(material_type=Material.MaterialType.FILE)
        material.file.name = "materials/konspekt.pdf"
        material.save()

        self.assertEqual(material.file_name, "konspekt.pdf")
        self.assertEqual(material.file_extension, "PDF")

    def test_youtube_embed_url_for_supported_links(self):
        watch = self._material(link="https://www.youtube.com/watch?v=VIDEOID123")
        short = self._material(link="https://youtu.be/VIDEOID123")

        self.assertEqual(
            watch.youtube_embed_url,
            "https://www.youtube.com/embed/VIDEOID123",
        )
        self.assertEqual(
            short.youtube_embed_url,
            "https://www.youtube.com/embed/VIDEOID123",
        )

    def test_youtube_embed_url_rejects_foreign_links(self):
        for link in ("https://evil.example.com/x", "https://vimeo.com/123"):
            with self.subTest(link=link):
                self.assertIsNone(self._material(link=link).youtube_embed_url)


class MaterialViewsTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="author02",
            email="author02@example.com",
            password="strong-password-123",
        )
        self.published = Material.objects.create(
            author=self.author,
            title="Опублікований матеріал",
            description="опис",
            category=Material.Category.CODES,
            material_type=Material.MaterialType.LINK,
            link="https://example.com",
            is_published=True,
        )
        self.hidden = Material.objects.create(
            author=self.author,
            title="Прихований матеріал",
            description="таємниця",
            category=Material.Category.CODES,
            material_type=Material.MaterialType.LINK,
            link="https://example.com",
            is_published=False,
        )

    def test_list_page_opens_and_uses_template(self):
        response = self.client.get(reverse("materials:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "materials/material_list.html")
        self.assertTemplateUsed(response, "core/base.html")

    def test_list_hides_unpublished_materials(self):
        response = self.client.get(reverse("materials:list"))

        self.assertContains(response, "Опублікований матеріал")
        self.assertNotContains(response, "Прихований матеріал")

    def test_list_shows_human_readable_categories(self):
        response = self.client.get(reverse("materials:list"))

        self.assertContains(response, "Шифри та коди")

    def test_empty_list_shows_message(self):
        Material.objects.all().delete()

        response = self.client.get(reverse("materials:list"))

        self.assertContains(response, "Навчальні матеріали поки не додані.")

    def test_detail_page_opens_for_published_material(self):
        response = self.client.get(
            reverse("materials:detail", args=[self.published.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "materials/material_detail.html")

    def test_detail_page_404_for_unpublished_material(self):
        response = self.client.get(
            reverse("materials:detail", args=[self.hidden.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_title_and_description_are_escaped(self):
        Material.objects.create(
            author=self.author,
            title="<script>alert(1)</script>",
            description="<img src=x onerror=alert(2)>",
            category=Material.Category.CODES,
            material_type=Material.MaterialType.LINK,
            link="https://example.com",
        )

        response = self.client.get(reverse("materials:list"))

        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertNotContains(response, "<img src=x onerror=alert(2)>")

    def test_pagination_is_nine_per_page(self):
        self.assertEqual(
            self.client.get(reverse("materials:list")).context["paginator"].per_page,
            9,
        )
