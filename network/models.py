from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="following")


class Post(models.Model):
    message = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField()
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")