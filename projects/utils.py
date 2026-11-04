from projects.models import Project


def get_projects_with_relations():
    return Project.objects.select_related("owner").prefetch_related("participants")
