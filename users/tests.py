import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from core.testing import BaseTestCase
from users.models import Skill

User = get_user_model()


class RegistrationAndLoginTests(BaseTestCase):
    def test_register_creates_user_with_avatar_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Анна",
                "surname": "Смирнова",
                "email": "Anna@Example.com",
                "password": self.password,
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        user = User.objects.get(email="anna@example.com")
        self.assertTrue(user.avatar.name.startswith("avatars/"))
        self.assertTrue(user.check_password(self.password))
        self.assertIsNone(user.phone)

    def test_two_users_without_phone_can_register(self):
        for email in ("first@example.com", "second@example.com"):
            self.client.post(
                reverse("users:register"),
                {"name": "А", "surname": "Б", "email": email, "password": self.password},
            )
        self.assertEqual(User.objects.count(), 2)

    def test_register_duplicate_email_shows_error(self):
        self.create_user("taken@example.com")
        response = self.client.post(
            reverse("users:register"),
            {"name": "А", "surname": "Б", "email": "TAKEN@example.com", "password": "x"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже зарегистрирован")

    def test_login_by_email(self):
        self.create_user("login@example.com")
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": self.password},
        )
        self.assertRedirects(response, reverse("projects:list"))

    def test_login_with_wrong_password_shows_error(self):
        self.create_user("login@example.com")
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "wrong"},
        )
        self.assertContains(response, "Неверный email или пароль")

    def test_logout_by_get(self):
        user = self.create_user("logout@example.com")
        self.client.force_login(user)
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("projects:list"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(BaseTestCase):
    def setUp(self):
        self.user = self.create_user("owner@example.com")
        self.client.force_login(self.user)

    def profile_data(self, **overrides):
        data = {
            "email": "owner@example.com",
            "name": "Пётр",
            "surname": "Петров",
            "about": "О себе",
            "phone": "89991234567",
            "github_url": "https://github.com/petrov",
        }
        data.update(overrides)
        return data

    def test_edit_profile_normalizes_phone(self):
        response = self.client.post(reverse("users:edit_profile"), self.profile_data())
        self.assertRedirects(response, reverse("users:detail", args=[self.user.pk]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79991234567")
        self.assertEqual(self.user.name, "Пётр")

    def test_phone_must_be_unique_across_formats(self):
        self.create_user("other@example.com", phone="+79991234567")
        response = self.client.post(reverse("users:edit_profile"), self.profile_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже используется")

    def test_invalid_phone_format(self):
        response = self.client.post(
            reverse("users:edit_profile"), self.profile_data(phone="12345")
        )
        self.assertContains(response, "8XXXXXXXXXX")

    def test_github_url_must_point_to_github(self):
        response = self.client.post(
            reverse("users:edit_profile"),
            self.profile_data(github_url="https://gitlab.com/petrov"),
        )
        self.assertContains(response, "GitHub")
        self.user.refresh_from_db()
        self.assertEqual(self.user.github_url, "")

    def test_edit_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("users:edit_profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_change_password(self):
        response = self.client.post(
            reverse("users:change_password"),
            {
                "old_password": self.password,
                "new_password1": "NewStrongPass456!",
                "new_password2": "NewStrongPass456!",
            },
        )
        self.assertRedirects(response, reverse("users:detail", args=[self.user.pk]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456!"))

    def test_owner_sees_edit_buttons(self):
        response = self.client.get(reverse("users:detail", args=[self.user.pk]))
        self.assertContains(response, "Добавить проект")
        self.assertContains(response, "add-skill-btn")

    def test_guest_does_not_see_edit_buttons(self):
        self.client.logout()
        response = self.client.get(reverse("users:detail", args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Добавить проект")
        self.assertNotContains(response, "add-skill-btn")


class SkillApiTests(BaseTestCase):
    def setUp(self):
        self.user = self.create_user("skills@example.com")
        self.other = self.create_user("other@example.com")
        self.client.force_login(self.user)
        self.add_url = reverse("users:skill_add", args=[self.user.pk])

    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type="application/json")

    def test_search_returns_ten_sorted_matches(self):
        for index in range(12):
            Skill.objects.create(name=f"Python {index:02d}")
        Skill.objects.create(name="Java")
        response = self.client.get(reverse("users:skill_search"), {"q": "py"})
        data = response.json()
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0], {"id": data[0]["id"], "name": "Python 00"})

    def test_add_new_skill_by_name(self):
        response = self.post_json(self.add_url, {"name": "Django"})
        data = response.json()
        self.assertTrue(data["created"])
        self.assertTrue(data["added"])
        self.assertEqual(data["name"], "Django")
        self.assertEqual(data["id"], data["skill_id"])
        self.assertTrue(self.user.skills.filter(name="Django").exists())

    def test_add_existing_skill_by_name_ignores_case(self):
        skill = Skill.objects.create(name="Python")
        data = self.post_json(self.add_url, {"name": "python"}).json()
        self.assertFalse(data["created"])
        self.assertEqual(data["skill_id"], skill.pk)

    def test_add_skill_by_id_twice(self):
        skill = Skill.objects.create(name="Go")
        first = self.post_json(self.add_url, {"skill_id": skill.pk}).json()
        second = self.post_json(self.add_url, {"skill_id": skill.pk}).json()
        self.assertTrue(first["added"])
        self.assertFalse(second["added"])

    def test_cannot_add_skill_to_other_user(self):
        url = reverse("users:skill_add", args=[self.other.pk])
        response = self.post_json(url, {"name": "Rust"})
        self.assertEqual(response.status_code, 403)

    def test_anonymous_gets_json_401(self):
        self.client.logout()
        response = self.post_json(self.add_url, {"name": "Rust"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "error")

    def test_remove_skill_keeps_it_in_db(self):
        skill = Skill.objects.create(name="SQL")
        self.user.skills.add(skill)
        url = reverse("users:skill_remove", args=[self.user.pk, skill.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.skills.filter(pk=skill.pk).exists())
        self.assertTrue(Skill.objects.filter(pk=skill.pk).exists())

    def test_remove_skill_user_does_not_have(self):
        skill = Skill.objects.create(name="SQL")
        url = reverse("users:skill_remove", args=[self.user.pk, skill.pk])
        self.assertEqual(self.client.post(url).status_code, 404)


class UserListTests(BaseTestCase):
    def test_pagination_and_order(self):
        users = [self.create_user(f"user{index}@example.com") for index in range(13)]
        response = self.client.get(reverse("users:list"))
        page = response.context["page_obj"]
        self.assertEqual(len(page.object_list), 12)
        self.assertEqual(page.object_list[0], users[-1])
        second = self.client.get(reverse("users:list"), {"page": 2})
        self.assertEqual(len(second.context["page_obj"].object_list), 1)

    def test_filter_by_skill_highlights_and_keeps_filter_in_pagination(self):
        skill = Skill.objects.create(name="C#")
        for index in range(13):
            user = self.create_user(f"dev{index}@example.com")
            user.skills.add(skill)
        self.create_user("noskill@example.com")
        response = self.client.get(reverse("users:list"), {"skill": "C#"})
        self.assertEqual(response.context["page_obj"].paginator.count, 13)
        self.assertEqual(response.context["active_skill"], "C#")
        self.assertContains(response, 'href="?skill=C%23"')
        self.assertContains(response, "filter-chip active")
        self.assertContains(response, "skill=C%23&amp;page=2")
        self.assertContains(response, "Сбросить")


class UxRegressionTests(BaseTestCase):
    def test_register_shows_success_message_on_login_page(self):
        response = self.client.post(
            reverse("users:register"),
            {"name": "Анна", "surname": "Б", "email": "new@example.com", "password": self.password},
            follow=True,
        )
        self.assertContains(response, "Аккаунт создан")

    def test_guest_has_no_account_menu(self):
        response = self.client.get(reverse("projects:list"))
        self.assertNotContains(response, "userSidebar")
        self.assertNotContains(response, "/users/None/")
        self.assertNotContains(response, "/users/logout/")

    def test_account_menu_trigger_is_button(self):
        user = self.create_user("menu@example.com")
        self.client.force_login(user)
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, 'aria-controls="userSidebar"')
        self.assertContains(
            response, 'id="userSidebar" class="user-sidebar" aria-label="Меню профиля" inert'
        )

    def test_viewport_meta_and_main_landmark(self):
        response = self.client.get(reverse("users:login"))
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, '<main id="main-content"')

    def test_forms_have_autocomplete(self):
        response = self.client.get(reverse("users:register"))
        for token in ("given-name", "family-name", 'autocomplete="email"', "new-password"):
            self.assertContains(response, token)
        user = self.create_user("auto@example.com")
        self.client.force_login(user)
        response = self.client.get(reverse("users:edit_profile"))
        self.assertContains(response, 'type="tel"')
        self.assertContains(response, 'aria-describedby="phone-hint"')

    def test_profile_title_contains_name_and_share_button_is_labelled(self):
        user = self.create_user("title@example.com", name="Ольга", surname="Орлова")
        response = self.client.get(reverse("users:detail", args=[user.pk]))
        self.assertContains(response, "<title>Ольга Орлова — TeamFinder</title>")
        self.assertContains(response, 'aria-label="Скопировать ссылку на профиль"')
        self.assertIn("csrftoken", response.cookies)

    def test_skill_filter_lists_all_skills_alphabetically(self):
        Skill.objects.create(name="Zig")
        Skill.objects.create(name="Ada")
        response = self.client.get(reverse("users:list"))
        names = [skill.name for skill in response.context["all_skills"]]
        self.assertEqual(names, ["Ada", "Zig"])
        empty = self.client.get(reverse("users:list"), {"skill": "Zig"})
        self.assertContains(empty, "Никого не нашлось")

    def test_spec_project_list_url_redirects(self):
        self.assertRedirects(
            self.client.get("/project/list/"), reverse("projects:list"), status_code=301
        )

    def test_participant_name_links_to_profile(self):
        user = self.create_user("link@example.com", name="Лев", surname="Львов")
        response = self.client.get(reverse("users:list"))
        self.assertContains(response, f'<a href="/users/{user.pk}/">Лев Львов</a>')

    def test_custom_404_page(self):
        response = self.client.get("/projects/999999/")
        self.assertContains(response, "Страница не найдена", status_code=404)
        self.assertContains(
            response, 'href="/projects/list/" class="black-button"', status_code=404
        )


class ProfileEmailTests(BaseTestCase):
    def setUp(self):
        self.user = self.create_user("me@example.com")
        self.client.force_login(self.user)

    def post(self, email):
        return self.client.post(
            reverse("users:edit_profile"),
            {"name": "Я", "surname": "Тест", "email": email, "about": "", "phone": "",
             "github_url": ""},
        )

    def test_owner_can_change_email_and_login_with_it(self):
        response = self.post("New@Example.com")
        self.assertRedirects(response, reverse("users:detail", args=[self.user.pk]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")
        self.client.logout()
        response = self.client.post(
            reverse("users:login"), {"email": "new@example.com", "password": self.password}
        )
        self.assertRedirects(response, reverse("projects:list"))

    def test_email_taken_by_other_user_is_rejected(self):
        self.create_user("taken@example.com")
        response = self.post("TAKEN@example.com")
        self.assertContains(response, "уже зарегистрирован")
