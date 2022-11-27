from django.contrib import admin

from core.admin import BaseAdmin
from posts.models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = (
        'title',
        'slug',
        'description',
    )
    search_fields = ('description',)
    list_filter = ('slug',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
