from typing import Type, Union

from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from base.services import IService

from users.services import UserService

from .models import Currency, Debit, Credit, Balance, Transfer
from django.contrib.auth.models import User


# нужно ли убрать операцию UPDATE и DELETE у транзакций?
class BalanceService(IService):
    model = Balance
    basequeryset = Balance.objects.all()


class CurrencyService(IService):
    model = Currency
    basequeryset = Currency.objects.all()


class TransferService(IService):
    model = Transfer
    basequeryset = Transfer.objects.all()


class DebitService(IService):
    model = Debit
    basequeryset = Debit.objects.all()


class CreditService(IService):
    model = Credit
    basequeryset = Debit.objects.all()


class OperationMixin:
    balance_service = BalanceService
    currency_service = CurrencyService
    transfer_service = TransferService
    debit_service = DebitService
    user_service = UserService
    credit_service = CreditService

    def validate_user_founds(
        self,
        user: User,
        currency: Currency,
        amount: float,
    ) -> None:
        balance = self.balance_service().fetch(
            user_id=user.id,
            currency_id=currency.id,
            value__gte=amount,
        ).first()

        if not balance:
            raise ValidationError(f'Not enough founds')

    def validate_balance_exists(
        self,
        user: User,
        currency: Currency,
        autocreate: bool = True,
    ) -> None:
        balance = self.balance_service().fetch(
            user_id=user.id,
            currency__name=currency.name,
        ).first()

        if not balance:
            if autocreate:
                self.balance_service().create(
                    user_id=user.id,
                    currency_id=currency.id,
                )
                return True
            raise ValidationError(f'No balance for currency {currency.name} avaliable for user {user.username}')

    def transfer(
        self,
        src_user_id: int,
        dst_user_id: int,
        currency_id: int,
        amount: float,
    ) -> Union[Transfer, None]:
        src_user = self.user_service().retrieve(src_user_id)
        dst_user = self.user_service().retrieve(dst_user_id)
        currency = self.currency_service().retrieve(currency_id)

        self.validate_balance_exists(
            user=src_user,
            currency=currency,
        )
        self.validate_balance_exists(
            user=dst_user,
            currency=currency,
        )
        self.validate_user_founds(
            user=src_user,
            currency=currency,
            amount=amount,
        )
        # балансы прошли валидацию, значит они 100% существуют и эксепшена быть не должно
        src_balance = self.balance_service().fetch(
            user_id=src_user.id,
            currency_id=currency.id,
        ).first()
        dst_balance = self.balance_service().fetch(
            user_id=dst_user.id,
            currency_id=currency.id,
        ).first()

        src_balance.value -= amount
        dst_balance.value += amount

        dst_balance.save()
        src_balance.save()

        transfer = self.transfer_service().create(
            src_user_id=src_user_id,
            dst_user_id=dst_user_id,
            amount=amount,
            currency_id=currency.id,
        )

        return transfer

    def debit(
        self,
        user_id: int,
        currency_id: int,
        amount: float,
    ) -> Union[Debit, None]:
        user = self.user_service().retrieve(user_id)
        currency = self.currency_service().retrieve(currency_id)

        self.validate_user_founds(
            user=user,
            currency=currency,
            amount=amount
        )

        balance = self.balance_service().fetch(
            user_id=user.id,
            currency_id=currency.id,
        ).first()

        balance.value -= amount

        debit = self.debit_service().create(
            user_id=user.id,
            amount=amount,
            currency_id=currency.id,
        )
        balance.save()

        return debit

    def credit(
        self,
        user_id: int,
        currency_id: int,
        amount: float,
    ) -> Union[Credit, None]:
        user = self.user_service().retrieve(user_id)
        currency = self.currency_service().retrieve(currency_id)

        self.validate_balance_exists(
            user=user,
            currency=currency,
        )

        balance = self.balance_service().fetch(
            user_id=user.id,
            currency_id=currency.id,
        ).first()

        balance.value += amount

        credit = self.credit_service().create(
            user_id=user.id,
            amount=amount,
            currency_id=currency.id,
        )
        balance.save()

        return credit


class OperationService(OperationMixin):
    balance_service = BalanceService

    def create_balances_for_user(self, user: User) -> QuerySet:
        currencies = self.currency_service().fetch().all()

        for currency in currencies:
            if len(self.balance_service().fetch(
                user_id=user.id,
                currency__name=currency.name
            ).all()) > 0:
                raise ValidationError(f'Already registred balance {currency.name} {user.username}')
            
            self.balance_service().create(
                    user_id=user.id,
                    currency_id=currency.id
                )
        
        return self.balance_service().fetch(user_id=user.id)
