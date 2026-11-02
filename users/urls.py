from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.user_list, name="list"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("skills/", views.skill_search, name="skill_search"),
    path("<int:pk>/", views.user_detail, name="detail"),
    path("<int:pk>/skills/add/", views.skill_add, name="skill_add"),
    path("<int:pk>/skills/add", views.skill_add),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.skill_remove,
        name="skill_remove",
    ),
]
