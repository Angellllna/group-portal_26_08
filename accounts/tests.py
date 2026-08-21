from django.contrib.auth import get_user_model
from django.contrib import admin
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import include, path, reverse
from django.views.generic import TemplateView

from .mixins import AdminRequiredMixin, ModeratorOrAdminRequiredMixin


class ModeratorOnlyView(ModeratorOrAdminRequiredMixin, TemplateView):
    template_name = "core/home.html"


class AdminOnlyView(AdminRequiredMixin, TemplateView):
    template_name = "core/home.html"


urlpatterns = [
    path("test/moderator/", ModeratorOnlyView.as_view(), name="test-moderator-view"),
    path("test/admin/", AdminOnlyView.as_view(), name="test-admin-view"),
    # маршрути проєкту потрібні, бо спільні шаблони (навбар) звертаються
    # до {% url %} інших модулів
    path("", include("config.urls")),
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


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="profileuser",
            first_name="Old",
            last_name="Name",
            email="profile@example.com",
            password="Str0ng!Pass#99",
            role=self.user_model.Role.MODERATOR,
        )
        self.other_user = self.user_model.objects.create_user(
            username="otheruser",
            password="Str0ng!Pass#99",
            role=self.user_model.Role.ADMIN,
        )

    def test_anonymous_user_cannot_open_private_profile(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )

    def test_authenticated_user_sees_own_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profileuser")
        self.assertContains(response, "Модератор")
        self.assertTemplateUsed(response, "accounts/profile_detail.html")

    def test_user_can_update_personal_data(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile-edit"),
            {
                "first_name": "New",
                "last_name": "Surname",
                "email": "new@example.com",
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.last_name, "Surname")
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.user.role, self.user_model.Role.MODERATOR)

    def test_profile_form_does_not_allow_role_or_admin_flags(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile-edit"),
            {
                "first_name": "New",
                "last_name": "Surname",
                "email": "new@example.com",
                "role": self.user_model.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, self.user_model.Role.MODERATOR)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_cannot_edit_another_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:profile-edit") + f"?user_id={self.other_user.pk}",
            {"first_name": "Changed", "last_name": "User", "email": "changed@example.com"},
        )

        self.assertRedirects(response, reverse("accounts:profile"))
        self.other_user.refresh_from_db()
        self.assertNotEqual(self.other_user.first_name, "Changed")

    def test_public_profile_hides_private_data(self):
        response = self.client.get(
            reverse("accounts:public-profile", kwargs={"pk": self.user.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profileuser")
        self.assertContains(response, "Модератор")
        self.assertNotContains(response, self.user.email)
        self.assertNotContains(response, "is_staff")
        self.assertTemplateUsed(response, "accounts/public_profile_detail.html")

    def test_admin_user_form_includes_role_field(self):
        user_admin = admin.site._registry[self.user_model]
        field_names = {
            field_name
            for _, fieldset in user_admin.fieldsets
            for field_name in fieldset["fields"]
        }

        self.assertIn("role", field_names)
