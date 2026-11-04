from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.forms import AdminUserChangeForm, AdminUserCreationForm
from users.models import Skill

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    ordering = ("-date_joined",)
    list_display = ("email", "name", "surname", "phone", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "name", "surname", "phone")
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("skills", "groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("name", "surname", "avatar", "about", "phone", "github_url", "skills")},
        ),
        (
            "Права доступа",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "password1", "password2"),
            },
        ),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
