
from django.urls import path

from . import views

app_name = 'network'
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("compose", views.compose, name="compose"),
    path("user/<int:user_id>", views.profile, name="profile"),
    path("following/", views.following, name="following"),
    path("toggle_like/<int:post_id>", views.toggle_like, name="toggle_like"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),

]
