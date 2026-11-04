from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from core.decorators import login_required_json
from core.http import json_error
from core.pagination import build_query_prefix, paginate
from projects.forms import ProjectForm
from projects.models import Project
from projects.utils import get_projects_with_relations


def project_list(request):
    projects = get_projects_with_relations()
    context = {
        "projects": projects,
        "page_obj": paginate(request, projects),
        "query_prefix": build_query_prefix(request),
    }
    return render(request, "projects/project_list.html", context)


@ensure_csrf_cookie
def project_detail(request, project_id):
    project = get_object_or_404(get_projects_with_relations(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
        messages.success(request, "Проект опубликован.")
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@require_POST
@login_required_json
def complete_project(request, project_id):
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return json_error("Проект не найден", HTTPStatus.NOT_FOUND)
    if project.owner_id != request.user.pk:
        return json_error("Завершить проект может только автор", HTTPStatus.FORBIDDEN)
    if not project.is_open:
        return json_error("Проект уже завершён", HTTPStatus.BAD_REQUEST)
    project.status = Project.Status.CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@require_POST
@login_required_json
def toggle_participate(request, project_id):
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return json_error("Проект не найден", HTTPStatus.NOT_FOUND)
    if project.owner_id == request.user.pk:
        return json_error("Автор не может покинуть свой проект", HTTPStatus.BAD_REQUEST)

    if is_participant := project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
    else:
        if not project.is_open:
            return json_error("Проект закрыт для новых участников", HTTPStatus.BAD_REQUEST)
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not is_participant})
