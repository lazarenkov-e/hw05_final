import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Post, User, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
        cls.group = mixer.blend('posts.Group', slug='test-group')
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
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.user_author,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post,
        )

        cls.index_url = ('posts:index', 'posts/index.html', None)
        cls.group_url = (
            'posts:group_list',
            'posts/group_list.html',
            cls.group.slug,
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            cls.user_author.username,
        )
        cls.post_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            cls.post.id,
        )
        cls.new_post_url = (
            'posts:post_create',
            'posts/create_post.html',
            None,
        )
        cls.edit_post_url = (
            'posts:post_edit',
            'posts/create_post.html',
            cls.post.id,
        )
        cls.paginated_urls = (
            cls.index_url,
            cls.group_url,
            cls.profile_url,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse(self.index_url[0]): self.index_url[1],
            reverse(
                self.group_url[0],
                args=(self.group_url[2],),
            ): self.group_url[1],
            reverse(
                self.profile_url[0],
                args=(self.profile_url[2],),
            ): self.profile_url[1],
            reverse(self.post_url[0], args=(self.post_url[2],)): self.post_url[
                1
            ],
            reverse(
                self.edit_post_url[0],
                args=(self.edit_post_url[2],),
            ): self.edit_post_url[1],
            reverse(self.new_post_url[0]): self.new_post_url[1],
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.anon.get(reverse(self.index_url[0]))
        expected = list(Post.objects.all()[: settings.NUMBER_OF_POSTS])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_show_correct_context(self):
        response = self.anon.get(
            reverse(self.group_url[0], args=(self.group_url[2],)),
        )
        expected = list(
            Post.objects.filter(group_id=self.group.id)[
                : settings.NUMBER_OF_POSTS
            ],
        )
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_show_correct_context(self):
        response = self.anon.get(
            reverse(self.profile_url[0], args=(self.profile_url[2],)),
        )
        expected = list(
            Post.objects.filter(author_id=self.user_author.id)[
                : settings.NUMBER_OF_POSTS
            ],
        )
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_show_correct_context(self):
        response = self.anon.get(
            reverse(self.post_url[0], args=(self.post_url[2],)),
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)
        self.assertEqual(self.post.comments.all()[0].text, self.comment.text)

    def test_create_edit_show_correct_context(self):
        response = self.auth.get(
            reverse(self.new_post_url[0]),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        response = self.author.get(
            reverse(self.edit_post_url[0], args=(self.edit_post_url[2],)),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_index_group_profile_after_create(self):
        reverse_page_names_post = {
            reverse(self.index_url[0]): self.group_url[2],
            reverse(
                self.group_url[0],
                args=(self.group_url[2],),
            ): self.group_url[2],
            reverse(
                self.profile_url[0],
                args=(self.profile_url[2],),
            ): self.group_url[2],
        }
        for value, expected in reverse_page_names_post.items():
            response = self.auth.get(value)
            for object in response.context['page_obj']:
                post_group = object.group.slug
                with self.subTest(value=value):
                    self.assertEqual(post_group, expected)

    def test_check_post_not_in_mistake_group_list(self):
        form_fields = {
            reverse(
                self.group_url[0],
                args=(self.group_url[2],),
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.auth.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_cash_index_page(self):
        cache.clear()
        response = self.auth.get(reverse(self.index_url[0]))
        cached_response = response.content
        post = mixer.blend('posts.Post')
        post.delete()
        response = self.auth.get(reverse(self.index_url[0]))
        self.assertEqual(response.content, cached_response)


class PaginatorViewsTest(TestCase):
    TEST_NUMBER_OF_POSTS = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User, username='user')
        cls.group = mixer.blend('posts.Group')
        cls.anon = Client()

        for post in range(15):
            Post.objects.create(
                text=f'Пост {post}',
                author=cls.user,
                group=cls.group,
            )

    def test_paginator_on_pages(self):
        posts_on_first_page = settings.NUMBER_OF_POSTS
        posts_on_second_page = 15 - settings.NUMBER_OF_POSTS
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        for page in url_pages:
            with self.subTest(page=page):
                self.assertEqual(
                    len(self.anon.get(page).context.get('page_obj')),
                    posts_on_first_page,
                )
                self.assertEqual(
                    len(
                        self.anon.get(page + '?page=2').context.get(
                            'page_obj',
                        ),
                    ),
                    posts_on_second_page,
                )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = mixer.blend(User, username='author')
        cls.follower = mixer.blend(User, username='follower')
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.author,
            text='Новый пост автора',
        )
        cls.auth = Client()
        cls.auth.force_login(cls.follower)

    def test_follower_user_can_follow_author(self):
        url = reverse('posts:profile_follow', args=(self.author,))
        self.auth.get(url)
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.author,
        ).exists())

    def test_follower_user_can_unfollow_author(self):
        Follow.objects.create(user=self.follower, author=self.author)
        url = reverse(
            'posts:profile_unfollow', args=(self.author,),
        )
        self.auth.get(url)

        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.author,
        ).exists())

    def test_new_authors_post_exists_in_followers_feed(self):
        Follow.objects.create(user=self.follower, author=self.author)
        url = reverse('posts:follow_index')
        response = self.auth.get(url)

        self.assertEqual(
            response.context['page_obj'][0].text, self.post.text,
        )

    def test_new_authors_post_notexists_in_unfollowers_feed(self):
        url = reverse('posts:follow_index')
        response = self.auth.get(url)

        self.assertFalse(
            response.context['page_obj'],
        )
