from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self) -> None:
        templates_url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.post.author}/',
            f'/posts/{self.post.pk}/',
        ]
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_edit_follow_urls_exists_at_desired_location(self) -> None:
        templates_url_names = [
            '/create/',
            f'/posts/{self.post.pk}/edit/',
            '/follow/',
        ]
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_found_page(self) -> None:
        response = self.client.get('/not_found/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self) -> None:
        templates_url_names = {
            'posts/index.html': '/',
            'posts/follow.html': '/follow/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.post.author}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            1: '/create/',
            2: f'/posts/{self.post.pk}/edit/',
        }
        for template, address in templates_url_names.items():
            if template is int:
                template = 'posts/create_post.html'
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)

                    self.assertTemplateUsed(
                        response,
                        template,
                        f"{template} doesn't work"
                    )
