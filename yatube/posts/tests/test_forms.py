import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post, User, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User, username='user')
        cls.user_author = mixer.blend(User, username='author')

        cls.anon = Client()
        cls.auth = Client()
        cls.author = Client()

        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.user_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_create_post(self):
        group = mixer.blend('posts.Group')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        data = {
            'text': 'Текст поста',
            'group': group.id,
            'image': uploaded,
        }
        self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, data['text'])
        self.assertEqual(post.group, group)
        self.assertEqual(post.image.name, 'posts/small.gif')

    def test_anon_cant_create_post(self):
        self.anon.post(
            reverse('posts:post_create'),
            {'text': 'Текст, которого нет'},
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_anon_cant_edit_post(self):
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый текст',
        )
        self.anon.post(
            reverse('posts:post_edit', args=(post.id,)),
            {'text': 'Текст, которого нет'},
            follow=True,
        )
        post.refresh_from_db()
        self.assertFalse(
            Post.objects.filter(text='Текст, которого нет').exists(),
        )
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.text, 'Тестовый текст')

    def test_author_can_edit_post(self):
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый текст',
        )
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.author.post(
            reverse('posts:post_edit', args=(post.id,)),
            {'text': 'Измененный текст', 'group': group.id},
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.text, 'Измененный текст')
        self.assertEqual(post.group, group)

    def test_auth_not_author_cant_edit_post(self):
        group = mixer.blend('posts.Group', slug='test-group')
        post = mixer.blend(
            'posts.Post',
            author=self.user_author,
            text='Тестовый текст',
        )

        self.auth.post(
            reverse('posts:post_edit', args=(post.id,)),
            {
                'text': 'Измененный тестовый текст',
                'group': group.id,
            },
            follow=True,
        )
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.group, None)

    def test_auth_can_add_comment(self):
        post = mixer.blend('posts.Post')
        comments_count = Comment.objects.count()
        comment_form = {
            'text': 'Текст',
        }
        self.auth.post(
            reverse('posts:add_comment', args=(post.id,)),
            data=comment_form,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_anon_cant_add_comment(self):
        post = mixer.blend('posts.Post')
        comments_count = Comment.objects.count()
        comment_form = {
            'text': 'Текст',
        }
        self.anon.post(
            reverse('posts:add_comment', args=(post.id,)),
            data=comment_form,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
