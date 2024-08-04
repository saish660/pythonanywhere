
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("posts", views.posts, name="all_posts"),
    path("user/<str:username>", views.profile, name="profile"),
    path("toggle_follow/<str:username>", views.toggle_follow, name="toggle_follow"),
    path("following", views.following_posts, name="following_posts"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("toggle_like", views.toggle_like, name="toggle_like")
]
