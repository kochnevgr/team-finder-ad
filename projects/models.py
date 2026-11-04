from django.conf import settings
from django.db import models

from core.constants import PROJECT_NAME_MAX_LENGTH, PROJECT_STATUS_MAX_LENGTH
from core.validators import validate_github_url


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    name = models.CharField("Название", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("GitHub", blank=True, validators=[validate_github_url])
    status = models.CharField(
        "Статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    @property
    def is_open(self):
        return self.status == self.Status.OPEN
