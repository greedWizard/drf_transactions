from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Credit, Currency, Debit, Transfer, Balance


class CurrencyBaseSerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = ['name']


class CurrencyReadSerializer(CurrencyBaseSerializer):
    class Meta(CurrencyBaseSerializer.Meta):
        fields = CurrencyBaseSerializer.Meta.fields + [
            'id'
        ]


class DebitBaseSerializer(ModelSerializer):
    class Meta:
        model = Debit
        fields = ['amount', ]


class DebitReadSerializer(DebitBaseSerializer):
    currency = CurrencyReadSerializer(many=False)
    
    class Meta(DebitBaseSerializer.Meta):
        fields = DebitBaseSerializer.Meta.fields + [
            'timestamp', 'currency'
        ]


class DebitPostSerializer(DebitBaseSerializer):
    user_id = serializers.IntegerField()
    currency_id = serializers.IntegerField()

    class Meta(DebitBaseSerializer.Meta):
        fields = DebitBaseSerializer.Meta.fields + [
            'user_id', 'currency_id',
        ]


class CreditBaseSerializer(ModelSerializer):
    class Meta:
        model = Credit
        fields = ['amount', ]


class CreditReadSerializer(CreditBaseSerializer):
    currency = CurrencyReadSerializer(many=False)
    
    class Meta(CreditBaseSerializer.Meta):
        fields = CreditBaseSerializer.Meta.fields + [
            'timestamp', 'currency',
        ]


class CreditPostSerializer(CreditBaseSerializer):
    user_id = serializers.IntegerField()
    currency_id = serializers.IntegerField()

    class Meta(CreditBaseSerializer.Meta):
        fields = CreditBaseSerializer.Meta.fields + [
            'user_id', 'currency_id',
        ]


class BalanceBaseSerializer(ModelSerializer):
    class Meta:
        model = Balance
        fields = ['value', ]


class BalanceReadSerializer(BalanceBaseSerializer):
    currency = CurrencyReadSerializer(many=False)

    class Meta(BalanceBaseSerializer.Meta):
        fields = BalanceBaseSerializer.Meta.fields + [
            'id', 'currency',
        ]


class TransferBaseSerializer(ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['amount']


class TransferReadSerializer(TransferBaseSerializer):
    currency = CurrencyReadSerializer(many=False)

    class Meta(TransferBaseSerializer.Meta):
        fields = TransferBaseSerializer.Meta.fields + [
            'id', 'timestamp', 'currency',
        ]


class TransferPostSerializer(TransferBaseSerializer):
    currency_id = serializers.IntegerField()
    amount = serializers.FloatField()
    src_user_id = serializers.IntegerField()
    dst_user_id = serializers.IntegerField()

    class Meta(TransferBaseSerializer.Meta):
        fields = TransferBaseSerializer.Meta.fields + [
            'currency_id', 'amount',
            'src_user_id', 'dst_user_id',
        ]