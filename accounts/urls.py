from django.urls import path
from .api import (
    AuthStatusAPIView,
    OverviewAPIView,
    BankAccountListAPIView,
    TransactionListAPIView,
    BillListAPIView,
    GoalListAPIView,
)

urlpatterns = [
    path('auth/status/', AuthStatusAPIView.as_view(), name='api_auth_status'),
    path('overview/', OverviewAPIView.as_view(), name='api_overview'),
    path('accounts/', BankAccountListAPIView.as_view(), name='api_accounts'),
    path('transactions/', TransactionListAPIView.as_view(), name='api_transactions'),
    path('bills/', BillListAPIView.as_view(), name='api_bills'),
    path('goals/', GoalListAPIView.as_view(), name='api_goals'),
]
