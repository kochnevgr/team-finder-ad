import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

User = get_user_model()

TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="team_finder_test_media_")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BaseTestCase(TestCase):
    password = "StrongPass123!"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def create_user(cls, email, name="Иван", surname="Иванов", **extra):
        return User.objects.create_user(
            email=email, password=cls.password, name=name, surname=surname, **extra
        )
