from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
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
            group=cls.group,
            text='Тестовая публикация',
        )
        cls.form = PostForm()

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author_client = Client()
        self.not_author = self.not_author_client.force_login(
            User.objects.create_user(username='not_author')
        )

    def test_create_post(self) -> None:
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст публикации',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        the_post = Post.objects.filter(text=form_data['text'])[0]
        last_post = Post.objects.all()[0]
        self.assertRedirects(response, (
            reverse('posts:profile', kwargs={'username': self.user.username})
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(the_post.text, last_post.text)
        self.assertEqual(the_post.group.id, last_post.group.id)

    def test_post_edit(self) -> None:
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст публикации',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.pk,
                author_id=self.user.id,
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )

    def test_guest_create_post(self):
        """Аноним не может добавить публикацию в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст публикации',
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_edit_post(self):
        """Аноним не может редактировать публикацию."""
        form_data = {
            'text': 'Отредактированный текст публикации',
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Post.objects.filter(
                id=self.post.pk,
                text=form_data['text'],
            ).exists()
        )

    def test_not_author_edit_post(self):
        """Не автор не может редактировать публикацию."""
        form_data = {
            'text': 'Отредактированный текст публикации',
        }
        response = self.not_author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Post.objects.filter(
                id=self.post.pk,
                author_id=User.objects.get(username='not_author').id,
                text=form_data['text'],
            ).exists(),
        )
