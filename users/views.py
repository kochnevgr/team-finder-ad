from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from core.decorators import login_required_json
from core.http import json_error, parse_request_data
from core.pagination import build_query_prefix, paginate
from projects.models import Project
from users.forms import LoginForm, ProfileForm, RegisterForm
from users.models import Skill, User

SKILL_SUGGESTIONS_LIMIT = 10
SKILL_NAME_MAX_LENGTH = Skill._meta.get_field("name").max_length


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Аккаунт создан. Войдите, чтобы продолжить.")
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_list(request):
    participants = User.objects.filter(is_active=True)
    active_skill = request.GET.get("skill", "").strip()
    if active_skill:
        participants = participants.filter(skills__name=active_skill).distinct()
    context = {
        "participants": participants,
        "page_obj": paginate(request, participants),
        "all_skills": Skill.objects.order_by("name"),
        "active_skill": active_skill,
        "query_prefix": build_query_prefix(request),
    }
    return render(request, "users/participants.html", context)


@ensure_csrf_cookie
def user_detail(request, pk):
    owned_projects = Project.objects.prefetch_related("participants")
    queryset = User.objects.prefetch_related(
        "skills",
        Prefetch("owned_projects", queryset=owned_projects),
    )
    profile = get_object_or_404(queryset, pk=pk)
    participated_projects = (
        profile.participated_projects.exclude(owner=profile)
        .select_related("owner")
        .prefetch_related("participants")
    )
    context = {"user": profile, "participated_projects": participated_projects}
    return render(request, "users/user-details.html", context)


@login_required
def edit_profile(request):
    profile = get_object_or_404(User, pk=request.user.pk)
    old_avatar = profile.avatar.name
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        if old_avatar and old_avatar != profile.avatar.name:
            profile.avatar.storage.delete(old_avatar)
        messages.success(request, "Профиль сохранён.")
        return redirect("users:detail", pk=profile.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль изменён.")
        return redirect("users:detail", pk=user.pk)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse([], safe=False)
    skills = (
        Skill.objects.filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:SKILL_SUGGESTIONS_LIMIT]
    )
    return JsonResponse(list(skills), safe=False)


@require_POST
@login_required_json
def skill_add(request, pk):
    if request.user.pk != pk:
        return json_error("Можно изменять только свои навыки", 403)

    data = parse_request_data(request)
    skill_id = data.get("skill_id")
    name = str(data.get("name") or "").strip()
    created = False

    if skill_id:
        try:
            skill = Skill.objects.filter(pk=int(skill_id)).first()
        except (TypeError, ValueError):
            return json_error("Некорректный идентификатор навыка", 400)
        if skill is None:
            return json_error("Навык не найден", 404)
    elif name:
        if len(name) > SKILL_NAME_MAX_LENGTH:
            return json_error("Слишком длинное название навыка", 400)
        skill, created = Skill.objects.get_or_create(
            name__iexact=name, defaults={"name": name}
        )
    else:
        return json_error("Не передан навык", 400)

    added = not request.user.skills.filter(pk=skill.pk).exists()
    if added:
        request.user.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.pk,
            "id": skill.pk,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@require_POST
@login_required_json
def skill_remove(request, pk, skill_id):
    if request.user.pk != pk:
        return json_error("Можно изменять только свои навыки", 403)
    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return json_error("Навык не найден", 404)
    if not request.user.skills.filter(pk=skill.pk).exists():
        return json_error("У пользователя нет такого навыка", 404)
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
