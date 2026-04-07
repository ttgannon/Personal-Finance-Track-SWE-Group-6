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
            'description',
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
            'name',
            'amount',
            'due_date',
            'status',
        ]


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            'id',
            'title',
            'category',
            'target_amount',
            'achieved_amount',
            'deadline',
        ]
