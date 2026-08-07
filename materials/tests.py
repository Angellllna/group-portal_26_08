from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

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
        self.assertIsNotNone(material.created_at)

    def test_str_returns_title(self):
        material = self._material()
        self.assertEqual(str(material), "Основи маскування")

    def test_author_is_linked_to_project_user_model(self):
        material = self._material()
        material.save()

        self.assertEqual(
            Material._meta.get_field("author").remote_field.model,
            get_user_model(),
        )
        self.assertEqual(list(self.author.materials.all()), [material])

    def test_material_without_file_and_link_is_rejected(self):
        material = self._material(link="")

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_blank_title_is_rejected(self):
        material = self._material(title="   ")

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_unknown_category_is_rejected(self):
        material = self._material(category="unknown")

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_ordering_is_newest_first(self):
        older = self._material(title="Старіший")
        older.save()
        newer = self._material(title="Новіший")
        newer.save()

        self.assertEqual(list(Material.objects.all()), [newer, older])
