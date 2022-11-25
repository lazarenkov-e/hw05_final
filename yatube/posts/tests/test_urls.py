from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = mixer.blend(User)
        cls.user_author = mixer.blend(User)
        cls.group = mixer.blend('posts.Group')
        cls.post = mixer.blend('posts.Post', author=cls.user_author)

        cls.anon = Client()
        cls.auth = Client()
        cls.author = Client()
        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.user_author)

        cls.urls = {
            'index': reverse('posts:index'),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'profile': reverse('posts:profile', args=(cls.user.username,)),
            'post': reverse('posts:post_detail', args=(cls.post.id,)),
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse('posts:post_edit', args=(cls.post.id,)),
            'missing': '/unexisting_page/',
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('index'), HTTPStatus.OK, self.anon),
            (self.urls.get('group'), HTTPStatus.OK, self.anon),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.anon),
            (self.urls.get('post'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('post_create'), HTTPStatus.OK, self.auth),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('post_edit'), HTTPStatus.OK, self.author),
        )
        for address, status, person in httpstatuses:
            with self.subTest(address=address):
                self.assertEqual(person.get(address).status_code, status)

    def test_templates(self) -> None:
        templates = (
            (self.urls.get('index'), 'posts/index.html', self.anon),
            (self.urls.get('group'), 'posts/group_list.html', self.anon),
            (self.urls.get('post'), 'posts/post_detail.html', self.anon),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.auth,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.author,
            ),
        )
        for address, template, person in templates:
            with self.subTest(template=template):
                self.assertTemplateUsed(person.get(address), template)

    def test_redirects(self) -> None:
        redirects = (
            (
                self.urls.get('post_create'),
                (
                    f'{reverse("users:login")}?next='
                    f'{self.urls.get("post_create")}'
                ),
                self.anon,
            ),
            (
                self.urls.get('post_edit'),
                f'{reverse("users:login")}?next={self.urls.get("post_edit")}',
                self.anon,
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post'),
                self.auth,
            ),
        )
        for address, redirect, person in redirects:
            with self.subTest(address=address):
                self.assertRedirects(person.get(address), redirect)

    def test_follow_url(self):
        author = mixer.blend(User)
        response = self.auth.get(
            f'/profile/{author.username}/follow/',
        )
        self.assertRedirects(response, f'/profile/{author.username}/')

    def test_unfollow_url(self):
        author = mixer.blend(User)
        Follow.objects.create(
            user=self.user,
            author=author,
        )
        response = self.auth.get(
            f'/profile/{author.username}/unfollow/',
        )
        self.assertRedirects(response, f'/profile/{author.username}/')
