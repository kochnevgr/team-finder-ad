from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username/repository"}
            ),
        }
