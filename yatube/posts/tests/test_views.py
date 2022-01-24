import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post
from ..views import POSTS_PER_PAGE

User = get_user_model()
# Для проверки паджинатора, количество постов > 10 (POSTS_PER_PAGE = 10)
POSTS_LIST = 52
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
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
        cls.follow = Follow.objects.create(
            author = cls.user,
            user = cls.follower,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.follower_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client.force_login(self.follower)

    def test_pages_uses_correct_template(self) -> None:
        """URL uses correct address."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/follow.html': reverse('posts:follow_index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': self.user.username
                })
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
            1: (
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
            ),
            2: reverse('posts:post_create'),
        }

        for template, reverse_name in templates_pages_names.items():
            if template is int:
                template = 'posts/create_post.html'
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(
                        response,
                        template,
                        f'Error in {template}'
                    )

    def test_post_view(self) -> None:
        """Not authorized client view post."""
        urls = {
            1: reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ),
            2: reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            3: reverse('posts:index'),
        }
        for key in urls.keys():
            with self.subTest(key=key):
                resp = self.client.get(urls[key])
                post_check = resp.context.get('page_obj')[0]
                the_post = Post.objects.get(
                    id=self.post.pk
                )
                self.assertEqual(
                    post_check,
                    the_post,
                    f'Error with not authorized client post view: {resp}.'
                )

    def test_post_detail_data(self) -> None:
        """post_detail context check."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        id_check = response.context.get('post').pk
        self.assertEqual(id_check, self.post.pk)

    def test_post_create_data(self) -> None:
        """post_create context check."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_data(self) -> None:
        """post_edit context check."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_follow_index_page(self) -> None:
        """Check follow index page"""
        resp = self.follower_client.get(reverse('posts:follow_index'))
        post_check = resp.context.get('page_obj')[0]
        the_post = Post.objects.get(
            id=self.post.pk
        )
        self.assertEqual(
            post_check,
            the_post,
            f'Error with follower client post view: {resp}.'
        )

    def test_cache_index_page(self) -> None:
        """Check cache works correct."""
        resp1 = self.client.get(reverse('posts:index'))
        check1 = resp1.content
        Post.objects.get(author=self.user).delete()
        resp2 = self.client.get(reverse('posts:index'))
        check2 = resp2.content
        self.assertEqual(Post.objects.count(), 0, 'The post is still in DB')
        self.assertEqual(check1, check2, "Cache doesn't work.")
        cache.clear()
        resp3 = self.client.get(reverse('posts:index'))
        check3 = resp3.content
        self.assertNotEqual(check1, check3, 'Cache is not cleared')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create([
            Post(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group
            )
            for i in range(1, POSTS_LIST + 1)
        ])
        cls.follow = Follow.objects.create(
            author = cls.user,
            user = cls.follower,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.follower_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client.force_login(self.follower)

    def test_first_page_contains_ten_records(self) -> None:
        """Template of first page with paginator."""
        urls = {
            1: reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ),
            2: reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            3: reverse('posts:index'),
        }
        for key in urls.keys():
            with self.subTest(key=key):
                resp = self.client.get(urls[key])
                self.assertEqual(
                    len(resp.context['page_obj']),
                    POSTS_PER_PAGE,
                    f'First {resp} page - paginator error.'
                )

    def test_second_page_contains_remainder_records(self) -> None:
        """Template of last index page with paginator."""
        urls = {
            1: reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ),
            2: reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            3: reverse('posts:index'),
        }
        for key in urls.keys():
            with self.subTest(key=key):
                resp = self.client.get(urls[key] + '?page=2')
                check = POSTS_LIST - POSTS_PER_PAGE
                if check >= POSTS_PER_PAGE:
                    self.assertEqual(
                        len(resp.context['page_obj']), POSTS_PER_PAGE,
                        f'Last {resp} page - paginator error(1).'
                    )
                else:
                    self.assertEqual(
                        len(resp.context['page_obj']),
                        POSTS_LIST % POSTS_PER_PAGE,
                        f'Last {resp} page - paginator error(2).'
                    )
    def test_first_follow_index_page(self) -> None:
        resp = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(resp.context['page_obj']),
            POSTS_PER_PAGE,
            f'First {resp} page - paginator error.'
        )
    
    def test_last_follow_index_page(self) -> None:
        resp = self.follower_client.get(reverse('posts:follow_index') + '?page=2')
        check = POSTS_LIST - POSTS_PER_PAGE
        if check >= POSTS_PER_PAGE:
            self.assertEqual(
                len(resp.context['page_obj']), POSTS_PER_PAGE,
                f'Last {resp} page - paginator error(1).'
            )
        else:
            self.assertEqual(
                len(resp.context['page_obj']),
                POSTS_LIST % POSTS_PER_PAGE,
                f'Last {resp} page - paginator error(2).'
            )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Valid form create post with image in Post."""
        posts_count = Post.objects.count()
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
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        the_post = Post.objects.get(
            text=form_data['text'],
            group=form_data['group'],
            image='posts/small.gif'
        )
        urls = {
            1: reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            2: reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            3: reverse('posts:index'),
        }
        resp_detail = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': the_post.id})
        )
        post_check = resp_detail.context.get('post')

        self.assertEqual(
            post_check,
            the_post,
            'Error with view in profile.'
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'NoName'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            the_post.text,
            form_data['text']
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif'
            ).exists(),
            'the_post does not exist in DB'
        )
        for key in urls.keys():
            print(urls[key])
            with self.subTest(key=key):
                resp = self.client.get(urls[key])
                post_check = resp.context.get('page_obj')[0]
                the_post = Post.objects.get(
                    text=form_data['text'],
                    image='posts/small.gif'
                )
                self.assertEqual(
                    post_check,
                    the_post,
                    f'Error with view in {resp}.'
                )
