from http import HTTPStatus

from django.test import Client, TestCase


class FoodgramAPITestCase(TestCase):
    """Тесты Foodgram."""

    def setUp(self):
        self.guest_client = Client()

    def test_recipes_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_list_exists(self):
        """Проверка доступности списка пользователей."""
        response = self.guest_client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
