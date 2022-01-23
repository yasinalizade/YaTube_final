from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая публикация',
        )

    def test_models_post_have_correct_object_names(self) -> None:
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        text = post.text[:15]
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(str(post), text)
        self.assertEqual(verbose, 'Текст')

    def test_model_group_have_correct_object_names(self) -> None:
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        title = group.title
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(str(group), title)
        self.assertEqual(verbose, 'Группа')

    def test_title_help_text(self) -> None:
        """help_text поля text совпадает с ожидаемым."""
        post = self.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')

    def test_title_help_text(self) -> None:
        """help_text поля title совпадает с ожидаемым."""
        group = self.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, 'Выберите группу')
