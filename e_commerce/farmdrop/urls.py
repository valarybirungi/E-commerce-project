from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("produce/", views.produce, name="produce"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("account/", views.customer_dashboard, name="customer_dashboard"),
]
