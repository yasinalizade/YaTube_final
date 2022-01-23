from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Comment, Follow, Post, Group, User
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


def index(request: HttpRequest) -> HttpResponse:
    """Index page."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'list_add': True,
        'group_add': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Group page."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'group_add': False,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Profile page."""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author=user).all()
    count = posts.count()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = None
    if request.user.is_authenticated:
        following = False
        if Follow.objects.filter(
            author=user,
            user=request.user
        ).exists():
            following = True
    context = {
        'author': user,
        'page_obj': page_obj,
        'count': count,
        'list_add': False,
        'group_add': True,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Post page."""
    post = get_object_or_404(Post, id=post_id)
    user = post.author_id
    count = Post.objects.filter(author=user).count()
    comments = Comment.objects.filter(post_id=post.id)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'count': count
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Create post."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)

    context = {
        "form": form,
        "is_edit": "Новый пост",
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Edit post."""
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if request.user != author:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id=post.pk)

    context = {
        "post": post,
        "form": form,
        "is_edit": "Редактировать пост",
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Comment."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Posts of people the user follows."""
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    count = posts.count()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'count': count,
        'list_add': True,
        'group_add': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Follow the author."""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user.is_authenticated,
        author=author).exists()
    if follow is False and author != request.user:
        Follow.objects.create(
            author=author,
            user=request.user,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Unfollow the author"""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(
        author=author,
        user=request.user
    ).delete()
    return redirect('posts:index')
