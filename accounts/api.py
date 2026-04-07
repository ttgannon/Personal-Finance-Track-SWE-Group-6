from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BankAccount, Transaction, Bill, Goal
from .serializers import (
    BankAccountSerializer,
    TransactionSerializer,
    BillSerializer,
    GoalSerializer,
)


class AuthStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'is_authenticated': True,
        })


class OverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = timezone.now()
        total_balance = (
            BankAccount.objects.filter(user=request.user).aggregate(total=Sum('balance'))['total']
            or 0
        )

        upcoming_bills = Bill.objects.filter(
            user=request.user,
            due_date__gte=current_date
        ).order_by('due_date')[:5]

        recent_transactions = Transaction.objects.filter(
            user=request.user,
            is_deleted=False
        ).order_by('-date')[:5]

        serializer = TransactionSerializer(recent_transactions, many=True)
        bill_serializer = BillSerializer(upcoming_bills, many=True)

        return Response({
            'total_balance': float(total_balance),
            'current_month': current_date.strftime('%B %Y'),
            'upcoming_bills': bill_serializer.data,
            'recent_transactions': serializer.data,
        })


class BankAccountListAPIView(generics.ListAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user, is_deleted=False).order_by('-date')


class BillListAPIView(generics.ListAPIView):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bill.objects.filter(user=self.request.user).order_by('due_date')


class GoalListAPIView(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
