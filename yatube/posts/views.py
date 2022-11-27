from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related('group'),
                settings.NUMBER_OF_POSTS,
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(request, posts, settings.NUMBER_OF_POSTS),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(request, posts, settings.NUMBER_OF_POSTS),
            'following': following,
        },
    )


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=post_id),
            'form': CommentForm(request.POST or None),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', form.instance.author)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
        },
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page = paginate(request, posts, settings.NUMBER_OF_POSTS)
    return render(request, 'posts/follow.html', {'page_obj': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username),
    ).delete()
    return redirect('posts:profile', username)
