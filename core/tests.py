from django.test import TestCase
from django.urls import resolve, reverse

from .views import HomePageView


class HomePageTests(TestCase):
    def test_home_url_is_root_and_named_home(self):
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(resolve("/").func.view_class, HomePageView)

    def test_home_page_opens_without_errors(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_core_templates(self):
        response = self.client.get(reverse("home"))

        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "core/base.html")

    def test_home_page_shows_required_title_and_text(self):
        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            "Антиказино: гра, у якій завжди виграє система",
        )
        self.assertContains(
            response,
            "Освітній портал про азартні механіки, психологічні маніпуляції,",
        )

    def test_base_template_provides_header_and_footer(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "<nav")
        self.assertContains(response, "<footer")
