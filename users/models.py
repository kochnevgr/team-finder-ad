from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from core.constants import (
    SKILL_NAME_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from core.validators import validate_github_url
from users.avatars import generate_avatar
from users.managers import UserManager


class Skill(models.Model):
    name = models.CharField("Название", max_length=SKILL_NAME_MAX_LENGTH)

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_skill_name_ci",
                violation_error_message="Такой навык уже существует.",
            ),
        ]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Email",
        unique=True,
        error_messages={"unique": "Пользователь с таким email уже зарегистрирован."},
    )
    name = models.CharField("Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        error_messages={"unique": "Этот номер телефона уже используется."},
    )
    github_url = models.URLField("GitHub", blank=True, validators=[validate_github_url])
    about = models.TextField("О себе", max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    skills = models.ManyToManyField(
        Skill,
        related_name="users",
        blank=True,
        verbose_name="Навыки",
    )
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)
    date_joined = models.DateTimeField("Дата регистрации", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-date_joined", "-id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if not self.phone:
            self.phone = None
        if not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)
