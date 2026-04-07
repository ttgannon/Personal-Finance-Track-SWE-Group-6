from rest_framework import serializers
from .models import BankAccount, Transaction, Bill, Goal


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id',
            'account_type',
            'account_name',
            'bank_name',
            'balance',
            'masked_account_number',
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'item_name',
            'shop_name',
            'amount',
            'date',
            'transaction_type',
            'category',
        ]


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'id',
            'item_name',
            'amount',
            'due_date',
        ]


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            'id',
            'title',
            'monthly_target',
            'achieved_amount',
        ]
