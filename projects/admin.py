from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description", "owner__email", "owner__surname")
    list_select_related = ("owner",)
    filter_horizontal = ("participants",)
    readonly_fields = ("created_at",)
