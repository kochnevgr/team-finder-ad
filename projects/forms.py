from django import forms

from projects.models import Project

STATUS_CHOICES = (
    (Project.Status.OPEN, "Открыт"),
    (Project.Status.CLOSED, "Закрыт"),
)


class ProjectForm(forms.ModelForm):
    status = forms.ChoiceField(label="Статус", choices=STATUS_CHOICES)

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username/repository"}
            ),
        }
