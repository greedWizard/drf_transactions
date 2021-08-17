from django.db.models.base import Model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

from balances.serializers import BalanceReadSerializer, CreditReadSerializer, DebitReadSerializer, TransferReadSerializer


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', ]


class UserReadSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            'id', 
        ]


class UserPostSerializer(UserBaseSerializer):
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            'password', 'repeat_password',
        ]


class UserWithHistorySerializer(UserBaseSerializer):
    debits = DebitReadSerializer(many=True)
    credits = CreditReadSerializer(many=True)
    transfers_sent = TransferReadSerializer(many=True)
    transfers_received = TransferReadSerializer(many=True)
    balances = BalanceReadSerializer(many=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            'debits', 'credits', 'balances',
            'transfers_sent', 'transfers_received',
        ]