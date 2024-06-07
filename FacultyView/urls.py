from . import views
from django.urls import path

urlpatterns = [
    path("portal/", views.faculty_view, name="faculty_view"),
    path("add_manually", views.add_manually, name="add_manually"),
    path("login/", views.login, name="login/"),
    path("faculty/", views.FacultyLogin, name="faculty/"),

]
