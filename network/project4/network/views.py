from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import User, Post


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def create_post(request):
    if request.method == "POST":
        message = request.POST["message"]
        user = request.user
        naive_timestamp = datetime.now()
        timezone_aware_timestamp = timezone.make_aware(naive_timestamp)
        
        post = Post(message=message, user=user, timestamp=timezone_aware_timestamp)
        post.save()
    
    return HttpResponseRedirect(reverse('index'))


def posts(request): 
    posts = Post.objects.order_by("-timestamp")
    return render(request, "network/posts.html", {
        "page": paginate(request, posts)
    })
    

def paginate(request, posts):
    try:
        page_num = int(request.GET.get('page_num'))
    except:
        page_num = 1
        
    pages = Paginator(posts, 10)
    if page_num > pages.num_pages:
        return HttpResponse("404 Page Not Found", status=404)

    return pages.page(page_num)


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        user = None
        
    if user is not None:
        if is_following(request.user, user):
            follow_action = "Unfollow"
        else:
            follow_action = "Follow"
        
        posts = Post.objects.filter(user=user).order_by("-timestamp")
        return render(request, "network/profile.html", {
            "requested_user": user,
            "page": paginate(request, posts),
            "followers_count": user.followers.count(),
            "following_count": user.following.count(),
            "action": follow_action,
            "is_superuser": user.is_superuser
        })
    else:
        return HttpResponse("User not found", status=404)
    

def is_following(user1, user2):
    return True if user2.followers.filter(username=user1.username) else False


def toggle_follow(request, username):
    follower = request.user
    target = User.objects.get(username=username)

    if is_following(request.user, target):
        target.followers.remove(follower)
        print("Unfollowed")
    else:
        target.followers.add(follower)
        print("followed")
        
    return HttpResponseRedirect(reverse("profile", kwargs={'username': username}))


@login_required
def following_posts(request):
    following_list = request.user.following.all()
    posts = Post.objects.filter(user__in = following_list).order_by("-timestamp")
    return render(request, "network/following.html", {
        "page": paginate(request, posts)
    })
    

@login_required
def edit_post(request):
    data = json.loads(request.body)
    new_message = data["new_message"]
    post_id = int(data["post_id"])
    post = Post.objects.get(id=post_id)
    if request.user == post.user:
        post.message = new_message
        post.save()
        return HttpResponse(status=200)
    return HttpResponse(status=403)


@login_required
def toggle_like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = int(data["post_id"])
        post = Post.objects.get(pk=post_id)
        
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            action = "disliked"
        else:
            post.likes.add(request.user)
            action = "liked"
        
        post.save()
        return JsonResponse({"like_count": post.likes.count(), "action": action})