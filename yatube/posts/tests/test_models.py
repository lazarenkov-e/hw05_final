from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from core.utils import truncatechars
from posts.models import MAX_LEN_TEXT, MAX_LEN_TITLE, Post

User = get_user_model()


class PostModelTest(TestCase):
    MODEL_INFO = (
        ('text', 'текст поста'),
        ('pub_date', 'дата публикации'),
        ('author', 'автор'),
        ('group', 'группа'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_correct_object_name(self):
        post = mixer.blend('posts.Post', text='10 simbols')
        self.assertEqual(post.text, str(post))

    def test_correct_object_long_name(self):
        post = mixer.blend('posts.Post', text='more than 15 simbols')
        self.assertEqual(
            truncatechars(post.text, MAX_LEN_TEXT),
            str(post),
        )

    def test_verbose_name(self):
        for value, expected in self.MODEL_INFO:
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_help_text(self):
        field_help_texts = (
            ('text', 'Введите текст поста'),
            ('group', 'Выберите группу'),
        )
        for value, expected in field_help_texts:
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text,
                    expected,
                )


class GroupModelTest(TestCase):
    GROUP_INFO = (
        ('title', 'Тестовая группа'),
        ('slug', 'Тестовый слаг'),
        ('description', 'тестовое описание'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_correct_object_name(self):
        test_group = mixer.blend('posts.Group', title='10 simbols')
        self.assertEqual(test_group.title, str(test_group))

    def test_correct_object_long_name(self):
        test_group = mixer.blend(
            'posts.Group',
            title='much more than 20 simbols',
        )
        self.assertEqual(
            truncatechars(test_group.title, MAX_LEN_TITLE),
            str(test_group),
        )
