from django.contrib.auth import get_user_model
from django.test import TestCase

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
