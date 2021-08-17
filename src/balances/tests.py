from django.test import TestCase
from .services import TransferService, CurrencyService, DebitService, CreditService, BalanceService, OperationService
from rest_framework.test import APIClient

from users.services import UserService
from pprint import pprint


# TODO: подправить внешний вид словарей на проверку json'а
# TODO: вынести тесты по отдельным каталогам (разделить на вьюхи и на сервисы)


class OperationsTestCase(TestCase):
    service = OperationService
    user_service = UserService
    currency_service = CurrencyService

    def setUp(self) -> None:
        user1 = self.user_service().create(
            username='user1',
            password='12345',
        )
        user2 = self.user_service().create(
            username='user2',
            password='12345',
        )
        self.currency_service().create(name='USD')

        self.service().create_balances_for_user(user1)
        self.service().create_balances_for_user(user2)

        assert len(user1.balances.all()) == len(self.currency_service().fetch().all())
        assert len(user2.balances.all()) == len(self.currency_service().fetch().all())

        self.service().credit(
            user_id=1,
            currency_id=1,
            amount=123,
        )

    def test_credit_operation(self):
        user = self.user_service().retrieve(1)
        currency = self.currency_service().retrieve(1)

        self.service().credit(
            user_id=user.id,
            currency_id=currency.id,
            amount=1000,
        )
        assert user.balances.first().value == 1123.0

    def test_debit_operation(self):
        user = self.user_service().retrieve(1)
        currency = self.currency_service().retrieve(1)

        self.service().debit(
            user_id=user.id,
            currency_id=currency.id,
            amount=123,
        )

        assert user.balances.first().value == 0

    def test_transfer_operation(self):
        src_user = self.user_service().retrieve(1)

        dst_user = self.user_service().retrieve(2)
        amount = 1000

        currency = self.currency_service().retrieve(1)

        self.tranfer = self.service().transfer(
            src_user_id=src_user.id,
            dst_user_id=dst_user.id,
            currency_id=currency.id,
            amount=0.5,
        )


class OprationViewTestCase(TestCase):
    service = OperationService
    user_service = UserService
    currency_service = CurrencyService
    client = APIClient

    def setUp(self) -> None:
        user1 = self.user_service().create(
            username='user1',
            password='12345',
        )
        user2 = self.user_service().create(
            username='user2',
            password='12345',
        )
        self.currency_service().create(name='USD')

        self.service().create_balances_for_user(user1)
        self.service().create_balances_for_user(user2)

        assert len(user1.balances.all()) == len(self.currency_service().fetch().all())
        assert len(user2.balances.all()) == len(self.currency_service().fetch().all())

        self.service().credit(
            user_id=1,
            currency_id=1,
            amount=123,
        )
    
    def test_debit_view(self):
        response = self.client.post(
            '/api/v1/balances/operations/debit/',
            data={
                'amount': 10,
                'user_id': 1,
                'currency_id': 1
            }
        )
        assert response.json() == {'amount': 10.0, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

    def test_credit_view(self):
        response = self.client.post(
            '/api/v1/balances/operations/credit/',
            data={
                'amount': 15,
                'user_id': 1,
                'currency_id': 1
            }
        )
        assert response.json() == {'amount': 15.0, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

    def test_transfer_view(self):
        response = self.client.post(
            '/api/v1/balances/operations/transfer/',
            data={
                'amount': 15,
                'src_user_id': 1,
                'dst_user_id': 1,
                'currency_id': 1,
            }
        )
        assert response.json() == {'amount': 15.0, 'id': 1, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

    def test_user_history(self):
        response = self.client.post(
            '/api/v1/balances/operations/debit/',
            data={
                'amount': 10,
                'user_id': 1,
                'currency_id': 1
            }
        )
        assert response.json() == {'amount': 10.0, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

        response = self.client.post(
            '/api/v1/balances/operations/credit/',
            data={
                'amount': 15,
                'user_id': 1,
                'currency_id': 1
            }
        )
        assert response.json() == {'amount': 15.0, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

        response = self.client.post(
            '/api/v1/balances/operations/transfer/',
            data={
                'amount': 15,
                'src_user_id': 1,
                'dst_user_id': 1,
                'currency_id': 1,
            }
        )
        assert response.json() == {'amount': 15.0, 'id': 1, 'timestamp': '2021-08-17', 'currency': {'name': 'USD', 'id': 1}}

        response = self.client.get(
            '/api/v1/balances/operations/history/',
            data={
                'user_id': 1,
            }
        )
        assert response.json() == {'balances': [{'currency': {'id': 1, 'name': 'USD'}, 'id': 1, 'value': 113.0}],
                                    'credits': [{'amount': 123.0,
                                                'currency': {'id': 1, 'name': 'USD'},
                                                'timestamp': '2021-08-17'},
                                                {'amount': 15.0,
                                                'currency': {'id': 1, 'name': 'USD'},
                                                'timestamp': '2021-08-17'}],
                                    'debits': [{'amount': 10.0,
                                                'currency': {'id': 1, 'name': 'USD'},
                                                'timestamp': '2021-08-17'}],
                                    'transfers_received': [{'amount': 15.0,
                                                            'currency': {'id': 1, 'name': 'USD'},
                                                            'id': 1,
                                                            'timestamp': '2021-08-17'}],
                                    'transfers_sent': [{'amount': 15.0,
                                                        'currency': {'id': 1, 'name': 'USD'},
                                                        'id': 1,
                                                        'timestamp': '2021-08-17'}],
                                    'username': 'user1'}