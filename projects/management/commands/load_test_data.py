from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project
from users.models import Skill

User = get_user_model()

TEST_PASSWORD = "TestPass123!"

TEST_USERS = (
    {
        "email": "anna@example.com",
        "name": "Анна",
        "surname": "Смирнова",
        "phone": "+79990000001",
        "github_url": "https://github.com/anna-smirnova",
        "about": "Backend-разработчица, люблю Django и чистые API.",
        "skills": ("Python", "Django", "PostgreSQL"),
        "projects": (
            {
                "name": "Трекер привычек",
                "description": "Веб-приложение для отслеживания привычек со статистикой "
                "и напоминаниями. Ищем фронтендера и дизайнера.",
                "github_url": "https://github.com/anna-smirnova/habit-tracker",
                "status": Project.Status.OPEN,
            },
        ),
    },
    {
        "email": "ivan@example.com",
        "name": "Иван",
        "surname": "Петров",
        "phone": "+79990000002",
        "github_url": "https://github.com/ivan-petrov",
        "about": "Фронтенд на React и TypeScript, немного дизайна.",
        "skills": ("JavaScript", "React", "TypeScript"),
        "projects": (
            {
                "name": "Книжный клуб онлайн",
                "description": "Платформа для обсуждения книг: клубы, голосования "
                "и календарь встреч.",
                "github_url": "",
                "status": Project.Status.OPEN,
            },
        ),
    },
    {
        "email": "maria@example.com",
        "name": "Мария",
        "surname": "Козлова",
        "phone": "+79990000003",
        "github_url": "",
        "about": "UI/UX-дизайнер, прототипирую в Figma.",
        "skills": ("Figma", "UI/UX"),
        "projects": (
            {
                "name": "Дизайн-система для стартапов",
                "description": "Открытый набор компонентов и гайдлайнов для быстрых MVP.",
                "github_url": "",
                "status": Project.Status.CLOSED,
            },
        ),
    },
    {
        "email": "dmitry@example.com",
        "name": "Дмитрий",
        "surname": "Соколов",
        "phone": "+79990000004",
        "github_url": "https://github.com/dmitry-sokolov",
        "about": "DevOps: Docker, CI/CD, мониторинг.",
        "skills": ("Docker", "Linux", "Python"),
        "projects": (
            {
                "name": "Бот для мониторинга серверов",
                "description": "Telegram-бот, который присылает алерты о нагрузке "
                "и доступности серверов.",
                "github_url": "https://github.com/dmitry-sokolov/monitoring-bot",
                "status": Project.Status.OPEN,
            },
        ),
    },
    {
        "email": "elena@example.com",
        "name": "Елена",
        "surname": "Новикова",
        "phone": "+79990000005",
        "github_url": "",
        "about": "Data Scientist, интересуюсь NLP.",
        "skills": ("Python", "Pandas", "Machine Learning"),
        "projects": (
            {
                "name": "Анализ отзывов о кафе",
                "description": "Сбор и анализ тональности отзывов о кафе города.",
                "github_url": "",
                "status": Project.Status.OPEN,
            },
        ),
    },
)

PARTICIPATION = {
    "ivan@example.com": ("Трекер привычек", "Анализ отзывов о кафе"),
    "maria@example.com": ("Трекер привычек", "Книжный клуб онлайн"),
    "dmitry@example.com": ("Трекер привычек",),
    "elena@example.com": ("Бот для мониторинга серверов",),
}

ADMIN_PROJECT = {
    "name": "Модерация TeamFinder",
    "description": "Служебный проект администратора платформы.",
    "github_url": "",
    "status": Project.Status.OPEN,
}


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, администратора и их проекты"

    @transaction.atomic
    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        self._create_admin()
        for data in TEST_USERS:
            user = self._get_or_create_user(data)
            self._add_skills(user, data["skills"])
            for project_data in data["projects"]:
                self._get_or_create_project(user, project_data)

        for email, project_names in PARTICIPATION.items():
            user = User.objects.get(email=email)
            for project in Project.objects.filter(name__in=project_names):
                project.participants.add(user)

        self._log(self.style.SUCCESS("Тестовые данные загружены"))

    def _log(self, message):
        if self.verbosity > 0:
            self.stdout.write(message)

    def _get_or_create_user(self, data):
        user = User.objects.filter(email=data["email"]).first()
        if user is not None:
            return user
        user = User.objects.create_user(
            email=data["email"],
            password=TEST_PASSWORD,
            name=data["name"],
            surname=data["surname"],
            phone=data["phone"],
            github_url=data["github_url"],
            about=data["about"],
        )
        self._log(f"Создан пользователь {user.email}")
        return user

    @staticmethod
    def _add_skills(user, skill_names):
        for skill_name in skill_names:
            skill, _ = Skill.objects.get_or_create(
                name__iexact=skill_name, defaults={"name": skill_name}
            )
            user.skills.add(skill)

    @staticmethod
    def _get_or_create_project(owner, data):
        project, _ = Project.objects.get_or_create(
            owner=owner,
            name=data["name"],
            defaults={
                "description": data["description"],
                "github_url": data["github_url"],
                "status": data["status"],
            },
        )
        project.participants.add(owner)
        return project

    def _create_admin(self):
        email = config("DJANGO_SUPERUSER_EMAIL", default="").strip().lower()
        password = config("DJANGO_SUPERUSER_PASSWORD", default="")
        if not email or not password:
            self._log(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_EMAIL и DJANGO_SUPERUSER_PASSWORD не заданы, "
                    "администратор не создан"
                )
            )
            return
        admin = User.objects.filter(email=email).first()
        if admin is None:
            admin = User.objects.create_superuser(
                email=email,
                password=password,
                name="Админ",
                surname="Тестовый",
            )
            self._log(f"Создан администратор {admin.email}")
        self._get_or_create_project(admin, ADMIN_PROJECT)
