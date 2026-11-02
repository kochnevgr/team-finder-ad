from django.core.management import call_command
from django.urls import reverse

from core.testing import BaseTestCase
from projects.models import Project
from users.models import User


class ProjectPagesTests(BaseTestCase):
    def setUp(self):
        self.owner = self.create_user("owner@example.com")
        self.other = self.create_user("other@example.com")

    def create_project(self, name="Проект", owner=None, **extra):
        project = Project.objects.create(name=name, owner=owner or self.owner, **extra)
        project.participants.add(project.owner)
        return project

    def test_root_redirects_to_project_list(self):
        response = self.client.get("/")
        self.assertRedirects(response, reverse("projects:list"))

    def test_list_pagination_and_order(self):
        projects = [self.create_project(f"Проект {index}") for index in range(13)]
        response = self.client.get(reverse("projects:list"))
        page = response.context["page_obj"]
        self.assertEqual(len(page.object_list), 12)
        self.assertEqual(page.object_list[0], projects[-1])

    def test_create_button_only_for_authenticated(self):
        self.create_project()
        self.assertNotContains(self.client.get(reverse("projects:list")), "+ Создать проект")
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("projects:list")), "+ Создать проект")

    def test_create_project_sets_owner_and_participant(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "Новый", "description": "", "github_url": "", "status": "open"},
        )
        project = Project.objects.get(name="Новый")
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))
        self.assertEqual(project.owner, self.owner)
        self.assertIn(self.owner, project.participants.all())

    def test_create_project_requires_name_and_github_link(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "", "github_url": "https://example.com/repo", "status": "open"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 0)
        self.assertIn("name", response.context["form"].errors)
        self.assertIn("github_url", response.context["form"].errors)

    def test_guest_cannot_create_project(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_edit_form_prefilled_and_saves(self):
        project = self.create_project("Старое имя")
        self.client.force_login(self.owner)
        url = reverse("projects:edit", args=[project.pk])
        response = self.client.get(url)
        self.assertTrue(response.context["is_edit"])
        self.assertEqual(response.context["form"].initial["name"], "Старое имя")
        response = self.client.post(url, {"name": "Новое имя", "status": "closed"})
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))
        project.refresh_from_db()
        self.assertEqual(project.name, "Новое имя")
        self.assertEqual(project.status, "closed")

    def test_only_owner_can_edit(self):
        project = self.create_project()
        self.client.force_login(self.other)
        response = self.client.get(reverse("projects:edit", args=[project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_detail_page(self):
        project = self.create_project("Детали", description="Описание")
        response = self.client.get(reverse("projects:detail", args=[project.pk]))
        self.assertContains(response, "Детали")
        self.assertContains(response, "Описание")
        self.assertNotContains(response, "participate-btn")


class ProjectActionsTests(BaseTestCase):
    def setUp(self):
        self.owner = self.create_user("owner@example.com")
        self.other = self.create_user("other@example.com")
        self.project = Project.objects.create(name="Проект", owner=self.owner)
        self.project.participants.add(self.owner)

    def test_owner_completes_project(self):
        self.client.force_login(self.owner)
        url = reverse("projects:complete", args=[self.project.pk])
        response = self.client.post(url)
        self.assertEqual(response.json(), {"status": "ok", "project_status": "closed"})
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_other_cannot_complete_project(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse("projects:complete", args=[self.project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate(self):
        self.client.force_login(self.other)
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        self.assertTrue(self.client.post(url).json()["participant"])
        self.assertIn(self.other, self.project.participants.all())
        self.assertFalse(self.client.post(url).json()["participant"])
        self.assertNotIn(self.other, self.project.participants.all())

    def test_owner_cannot_leave_project(self):
        self.client.force_login(self.owner)
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_cannot_join_closed_project(self):
        self.project.status = Project.Status.CLOSED
        self.project.save()
        self.client.force_login(self.other)
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_guest_gets_json_401(self):
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "error")


class LoadTestDataTests(BaseTestCase):
    def test_command_is_idempotent_and_every_user_has_project(self):
        call_command("load_test_data", verbosity=0)
        call_command("load_test_data", verbosity=0)
        self.assertGreaterEqual(User.objects.count(), 5)
        for user in User.objects.all():
            self.assertTrue(user.owned_projects.exists(), user.email)


class ProjectUxTests(BaseTestCase):
    def setUp(self):
        self.owner = self.create_user("owner@example.com")
        self.member = self.create_user("member@example.com", name="Мира", surname="Участникова")
        self.project = Project.objects.create(name="Проект", owner=self.owner)
        self.project.participants.add(self.owner, self.member)

    def test_profile_lists_participated_projects(self):
        response = self.client.get(reverse("users:detail", args=[self.member.pk]))
        self.assertContains(response, "Участвует в проектах (1)")
        self.assertContains(response, f'href="/projects/{self.project.pk}/">Проект</a>')

    def test_closed_project_hides_join_button_for_new_users(self):
        self.project.status = Project.Status.CLOSED
        self.project.save()
        outsider = self.create_user("outsider@example.com")
        self.client.force_login(outsider)
        response = self.client.get(reverse("projects:detail", args=[self.project.pk]))
        self.assertNotContains(response, "participate-btn")
        self.assertContains(response, "набор участников закрыт")
        self.assertContains(response, "is-closed")

    def test_closed_project_still_allows_member_to_leave(self):
        self.project.status = Project.Status.CLOSED
        self.project.save()
        self.client.force_login(self.member)
        response = self.client.get(reverse("projects:detail", args=[self.project.pk]))
        self.assertContains(response, "Отказаться от участия")

    def test_guest_sees_login_prompt_and_csrf_cookie_is_set(self):
        response = self.client.get(reverse("projects:detail", args=[self.project.pk]))
        self.assertContains(response, "Войти, чтобы участвовать")
        self.assertIn("csrftoken", response.cookies)

    def test_create_shows_message_and_edit_cancel_returns_to_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "Новый", "description": "", "github_url": "", "status": "open"},
            follow=True,
        )
        self.assertContains(response, "Проект опубликован")
        response = self.client.get(reverse("projects:edit", args=[self.project.pk]))
        self.assertContains(response, f'href="/projects/{self.project.pk}/" class="cancel-button"')

    def test_custom_403_page(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("projects:edit", args=[self.project.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Нет доступа", status_code=403)
