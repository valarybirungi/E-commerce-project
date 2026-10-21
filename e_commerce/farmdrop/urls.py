from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("produce/", views.produce, name="produce"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
