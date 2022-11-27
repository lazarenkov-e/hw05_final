from django.contrib.auth import get_user_model
from django.db import models

from core.utils import truncatechars

User = get_user_model()

MAX_LEN_TITLE = 20
MAX_LEN_TEXT = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return truncatechars(self.title, MAX_LEN_TITLE)


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return truncatechars(self.text, MAX_LEN_TEXT)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='комментарий',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='Введите текст комментария',
    )

    created = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        verbose_name = 'подписка'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
