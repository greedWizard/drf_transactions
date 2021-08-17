from django.core import validators
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.deletion import CASCADE


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Balance(models.Model):
    user = models.ForeignKey(
        to=User, 
        related_name='balances', 
        on_delete=models.CASCADE
    )
    currency = models.ForeignKey(
        to=Currency,
        related_name='balances',
        on_delete=models.CASCADE
    )
    value = models.FloatField(
        validators=[
            MinValueValidator(0),
        ],
        default=0.0,
    )


class Debit(models.Model):
    currency = models.ForeignKey(
        to=Currency,
        related_name='debits',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to=User,
        related_name='debits',
        on_delete=models.CASCADE,
    )
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    timestamp = models.DateField(auto_now=True)


class Credit(models.Model):
    currency = models.ForeignKey(
        to=Currency,
        related_name='credits',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to=User,
        related_name='credits',
        on_delete=models.CASCADE,
    )
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    timestamp = models.DateField(auto_now=True)


class Transfer(models.Model):
    currency = models.ForeignKey(
        to=Currency,
        related_name='transfers',
        on_delete=models.CASCADE,
    )
    src_user = models.ForeignKey(
        to=User,
        related_name='transfers_sent',
        on_delete=models.CASCADE,
    )
    dst_user = models.ForeignKey(
        to=User,
        related_name='transfers_received',
        on_delete=models.CASCADE,
    )
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    timestamp = models.DateField(auto_now=True)
