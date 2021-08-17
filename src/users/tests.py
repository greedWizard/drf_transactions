from .urls import router
from django.test import TestCase
from .services import UserService
from rest_framework.test import APIClient


TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'a1b23cjk'


class UserServiceTestCase(TestCase):
    service = UserService
    
    def setUp(self) -> None:
        self.user = self.service().create(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            repeat_password=TEST_PASSWORD,
        )

    def test_user_created(self):
        user = self.service().fetch(username='testuser').first()
        assert user.username == TEST_USERNAME

    def test_user_updated(self):
        user = self.service().update(
            { 'username': '12345' },
            username=TEST_USERNAME
        ).first()
        assert user.username == '12345'

    def test_user_deleted(self):
        self.service().fetch().delete()

        assert len(self.service().basequeryset) == 0


class UserViewTestCase(TestCase):
    service = UserService
    client = APIClient()

    def setUp(self) -> None:
        self.user = self.service().create(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            repeat_password=TEST_PASSWORD,
        )
    
    def test_create_view(self):
        response = self.client.get('/api/v1/users/')
        assert response.json() == [{'username': 'testuser', 'id': 1}]

    def test_retrieve_user(self):
        response = self.client.get('/api/v1/users/1/')
        assert response.json() == {'username': 'testuser', 'id': 1}
    
    def test_update_user(self):
        response = self.client.put(
            '/api/v1/users/1/',
            data={
                'username': '12345',
                'password': TEST_PASSWORD,
                'repeat_password': TEST_PASSWORD,
            },
            content_type='application/json'
        )
        assert response.json() == {'username': '12345', 'id': 1}

    def test_delete_user(self):
        response = self.client.delete(
            '/api/v1/users/1/'
        )
        assert response.json() == {'status': 'success'}
        assert len(self.service().basequeryset) == 0
