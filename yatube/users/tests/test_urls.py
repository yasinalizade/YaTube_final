from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class TaskURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/logged_out.html': '/auth/logout/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_complete.html': '/auth/reset/done/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self) -> None:
        """Работоспособность URL-адресов."""
        templates_url_names = [
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
        ]
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_form(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(
            response.template_name[0], 'users/password_reset_form.html'
        )
        response = self.authorized_client.post(
            reverse('password_reset'),
        )
        response = self.authorized_client.get(
            reverse('password_reset_confirm', kwargs={
                'token': 'token',
                'uidb64': 'uid',
            })
        )
        self.assertEqual(
            response.template_name[0],
            'users/password_reset_confirm.html'
        )
        response = self.authorized_client.post(
            reverse('password_reset_confirm', kwargs={
                'token': 'token',
                'uidb64': 'uid',
            }),
            {'new_password1': 'pass', 'new_password2': 'pass'}
        )
        self.assertEqual(response.status_code, 200)
