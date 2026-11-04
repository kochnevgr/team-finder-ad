# TeamFinder
**Кочнев Егор** 
**Github: kochnevgr**


Платформа для поиска единомышленников для pet-проектов. Пользователи публикуют проекты, присоединяются к чужим, указывают свои навыки и ищут участников по навыкам (вариант 2).

## Технологии

- Python 3.12, Django 5.2
- PostgreSQL 16
- Gunicorn, Nginx
- Docker, Docker Compose
- GitHub Actions (flake8, тесты, сборка образа в GHCR, деплой по SSH)

## Запуск в Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Сайт: http://localhost:8000, админка: http://localhost:8000/admin/

При старте автоматически применяются миграции, собирается статика и загружаются тестовые данные (`LOAD_TEST_DATA=True`). Данные БД и загруженные аватары хранятся в volumes `pg_data` и `media_data`.

Тестовые пользователи (пароль у всех `TestPass123!`), у каждого есть проект:

| Email | Имя |
|---|---|
| anna@example.com | Анна Смирнова |
| ivan@example.com | Иван Петров |
| maria@example.com | Мария Козлова |
| dmitry@example.com | Дмитрий Соколов |
| elena@example.com | Елена Новикова |

Администратор создаётся из переменных `DJANGO_SUPERUSER_EMAIL` и `DJANGO_SUPERUSER_PASSWORD` в `.env`.

Остановка: `docker compose down` (с удалением данных: `docker compose down -v`).

## Локальный запуск без Docker для приложения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db
python manage.py migrate
python manage.py load_test_data
python manage.py runserver
```

Тесты: `python manage.py test`, проверка стиля: `flake8 .`

## Деплой на сервер

На сервере нужны Docker и Docker Compose, в каталоге `DEPLOY_PATH` должен лежать заполненный `.env` (`DJANGO_DEBUG=False`, свои `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `LOAD_TEST_DATA=False`).

В репозитории GitHub задать:

- secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `SSH_PORT` (необязательно), `DEPLOY_PATH`;
- variable: `DEPLOY_ENABLED=true`.

