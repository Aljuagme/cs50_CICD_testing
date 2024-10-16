import json
from lib2to3.fixes.fix_input import context

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by('-created')
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts_list = paginator.page(page_number)
    except PageNotAnInteger:
        posts_list = paginator.page(1)
    except EmptyPage:
        posts_list = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "Posts": posts_list})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


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
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


@login_required
def compose(request):
    print(request.user.id)
    if request.method == "POST":
        print("I am reaching this point")
        try:
            data = json.loads(request.body)
            print("Data form compose: ", data)

            post = Post(
                author = request.user,
                body = data["body"]
            )
            post.save()

            return JsonResponse({"message": "Post created successfully."}, status=201)
        except KeyError:
            return JsonResponse({"error": "Invalid data."}, status=400)
    return JsonResponse({"error": "POST request required."}, status=400)


@login_required
def handle_followers(request, user_id):
    if request.method == "POST":
        try:
            viewed_user = get_object_or_404(User, pk=user_id)

            data = json.loads(request.body)
            action = data["action"]

            if action == "follow":
                viewed_user.following.add(request.user)
                return JsonResponse({"message": "Following user has been added."}, status=201)
            elif action == "unfollow":
                viewed_user.following.remove(request.user)
                return JsonResponse({"message": "Unfollowing user has been removed."}, status=201)
            else:
                return JsonResponse({"error": "Invalid action."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST request required."}, status=400)




@login_required
def emails(request):
    pass




@login_required
def profile(request, user_id):
    # IMPROVE!
    user = request.user
    viewed_user = get_object_or_404(User, pk=user_id)
    is_following = user.follows.filter(pk=user_id).exists()

    if request.method == "POST":
        current_user_profile = request.user
        if user_id != current_user_profile.id:
            if is_following:
                user.follows.remove(viewed_user)
                is_following = False

            else:
                user.follows.add(viewed_user)
                is_following = True

            context = {
                "user": user,
                "viewed_user": viewed_user,
                "is_following": is_following
            }

            user.save()
            return render(request, "network/profile.html", context)

    return render(request, "network/profile.html", {
        "user": request.user,
        "viewed_user": viewed_user,
        "is_following": is_following
    })


def following(request):
    user = request.user
    followed_users = user.follows.all()

    posts = Post.objects.filter(author__in=followed_users).order_by("-created")

    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts_list = paginator.page(page_number)
    except PageNotAnInteger:
        posts_list = paginator.page(1)
    except EmptyPage:
        posts_list = paginator.page(paginator.num_pages)

    context = {
        "user": user,
        "Posts": posts_list
    }

    return render(request, "network/index.html", context)


@login_required()
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count()
    })


def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            post = get_object_or_404(Post, pk=post_id)
            #new_content = request.POST["body"] # request.POST only for "FORMS"

            # Parse the request body as JSON
            data = json.loads(request.body.decode('utf-8'))  # Safely decode request body
            new_content = data.get("body", "")  # Get the 'body' field from the JSON data

            if new_content:
                post.body = new_content
                post.save()
                return JsonResponse({"Success": True, "message": "Post edited successfully."}, status=201)
            else:
                return JsonResponse({"Success": False, "message": "Content cannot be empty"}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"Success": False, "message": "Post does not exist."}, status=400)
    else:
        return JsonResponse({"Success": False, "message": "Invalid request method."}, status=400)

