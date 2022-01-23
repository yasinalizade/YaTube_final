from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase


class StaticURLTests(TestCase):

    def test_author_exists_at_desired_location(self) -> None:
        """Проверка доступности адреса /about/author/."""
        response = self.client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_author_url_uses_correct_template(self) -> None:
        """Проверка шаблона для адреса /about/author/."""
        response = self.client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_auth_view_url_accessible_by_name(self) -> None:
        """Проверка доступности view-функции по имени author."""
        response = self.client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_auth_view_url_uses_correct_template(self) -> None:
        """Проверка шаблона view-функции по имени auth."""
        response = self.client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_exists_at_desired_location_(self) -> None:
        """Проверка доступности адреса /about/tech/."""
        response = self.client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_url_uses_correct_template(self) -> None:
        """Проверка шаблона для адреса /about/tech/."""
        response = self.client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')

    def test_tech_view_url_accessible_by_name(self) -> None:
        """Проверка доступности view-функции по имени tech."""
        response = self.client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_view_url_uses_correct_template(self) -> None:
        """Проверка шаблона view-функции по имени tech."""
        response = self.client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
