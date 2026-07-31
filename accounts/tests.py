from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Profile


class ProfileModelTests(TestCase):
    def test_profile_is_created_with_expected_fields(self):
        user = get_user_model().objects.create_user(
            username="cadet01",
            email="cadet01@example.com",
            password="strong-password-123",
        )

        profile = Profile.objects.create(
            user=user,
            role="cadet",
            codename="Ghost",
            bio="Training cadet",
        )

        self.assertEqual(profile.user.username, "cadet01")
        self.assertEqual(profile.role, "cadet")
        self.assertEqual(profile.codename, "Ghost")
        self.assertEqual(profile.bio, "Training cadet")
