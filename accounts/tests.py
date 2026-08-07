from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import path, reverse
from django.views.generic import TemplateView

from .mixins import AdminRequiredMixin, ModeratorOrAdminRequiredMixin


class ModeratorOnlyView(ModeratorOrAdminRequiredMixin, TemplateView):
    template_name = "home.html"


class AdminOnlyView(AdminRequiredMixin, TemplateView):
    template_name = "home.html"


urlpatterns = [
    path("test/moderator/", ModeratorOnlyView.as_view(), name="test-moderator-view"),
    path("test/admin/", AdminOnlyView.as_view(), name="test-admin-view"),
]

class UserModelTests(TestCase):
    def test_default_role_is_user(self):
        user = get_user_model().objects.create_user(
            username="student01",
            email="student01@example.com",
            password="strong-password-123",
        )

        self.assertEqual(user.role, get_user_model().Role.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_is_moderator_role(self):
        moderator = get_user_model().objects.create_user(
            username="mod01",
            email="mod01@example.com",
            password="strong-password-123",
            role=get_user_model().Role.MODERATOR,
        )

        self.assertTrue(moderator.is_moderator_role())

    def test_is_admin_role_for_admin_and_staff_and_superuser(self):
        admin_by_role = get_user_model().objects.create_user(
            username="admin_by_role",
            email="admin_role@example.com",
            password="strong-password-123",
            role=get_user_model().Role.ADMIN,
        )
        admin_by_staff = get_user_model().objects.create_user(
            username="admin_by_staff",
            email="admin_staff@example.com",
            password="strong-password-123",
            role=get_user_model().Role.USER,
            is_staff=True,
        )
        admin_by_superuser = get_user_model().objects.create_superuser(
            username="admin_by_superuser",
            email="admin_super@example.com",
            password="strong-password-123",
        )

        self.assertTrue(admin_by_role.is_admin_role())
        self.assertTrue(admin_by_staff.is_admin_role())
        self.assertTrue(admin_by_superuser.is_admin_role())

    def test_can_moderate(self):
        regular_user = get_user_model().objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="strong-password-123",
            role=get_user_model().Role.USER,
        )
        moderator = get_user_model().objects.create_user(
            username="moderator_user",
            email="moderator@example.com",
            password="strong-password-123",
            role=get_user_model().Role.MODERATOR,
        )
        admin = get_user_model().objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="strong-password-123",
            role=get_user_model().Role.ADMIN,
        )

        self.assertFalse(regular_user.can_moderate())
        self.assertTrue(moderator.can_moderate())
        self.assertTrue(admin.can_moderate())


@override_settings(ROOT_URLCONF="accounts.tests", LOGIN_URL="/login/")
class AccessMixinsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.regular_user = self.user_model.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="strong-password-123",
            role=self.user_model.Role.USER,
        )
        self.moderator = self.user_model.objects.create_user(
            username="moderator",
            email="moderator@test.com",
            password="strong-password-123",
            role=self.user_model.Role.MODERATOR,
        )
        self.admin_by_role = self.user_model.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="strong-password-123",
            role=self.user_model.Role.ADMIN,
        )
        self.superuser = self.user_model.objects.create_superuser(
            username="superuser",
            email="super@test.com",
            password="strong-password-123",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("test-moderator-view"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login/?next="))

    def test_regular_user_is_denied_moderator_access(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse("test-moderator-view"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response,
            "У вас немає прав для виконання цієї дії.",
            status_code=403,
        )

    def test_moderator_passes_moderator_or_admin_mixin(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("test-moderator-view"))

        self.assertEqual(response.status_code, 200)

    def test_moderator_is_denied_admin_mixin(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("test-admin-view"))

        self.assertEqual(response.status_code, 403)

    def test_admin_passes_both_mixins(self):
        self.client.force_login(self.admin_by_role)

        moderator_response = self.client.get(reverse("test-moderator-view"))
        admin_response = self.client.get(reverse("test-admin-view"))

        self.assertEqual(moderator_response.status_code, 200)
        self.assertEqual(admin_response.status_code, 200)

    def test_superuser_passes_both_mixins(self):
        self.client.force_login(self.superuser)

        moderator_response = self.client.get(reverse("test-moderator-view"))
        admin_response = self.client.get(reverse("test-admin-view"))

        self.assertEqual(moderator_response.status_code, 200)
        self.assertEqual(admin_response.status_code, 200)


class RegisterViewTests(TestCase):
    def test_register_creates_user_with_role_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "Str0ng!Pass#99",
                "password2": "Str0ng!Pass#99",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        user = get_user_model().objects.get(username="newuser")
        self.assertEqual(user.role, get_user_model().Role.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_register_role_cannot_be_set_via_post(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "hacker",
                "email": "hacker@example.com",
                "password1": "Str0ng!Pass#99",
                "password2": "Str0ng!Pass#99",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user = get_user_model().objects.filter(username="hacker").first()
        if user:
            self.assertEqual(user.role, get_user_model().Role.USER)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    def test_register_page_loads(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="Str0ng!Pass#99",
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_redirects_on_success(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "loginuser", "password": "Str0ng!Pass#99"},
        )

        self.assertRedirects(response, reverse("home"))

    def test_logout_redirects_to_home(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("home"))
