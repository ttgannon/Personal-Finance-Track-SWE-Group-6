from django.urls import path
from .api import (
    AuthStatusAPIView,
    OverviewAPIView,
    BankAccountListAPIView,
    TransactionListAPIView,
    BillListAPIView,
    GoalListAPIView,
)
from . import plaid_views

urlpatterns = [
    # ── REST API ──────────────────────────────────────────────────────────────
    path('auth/status/',    AuthStatusAPIView.as_view(),       name='api_auth_status'),
    path('overview/',       OverviewAPIView.as_view(),          name='api_overview'),
    path('accounts/',       BankAccountListAPIView.as_view(),   name='api_accounts'),
    path('transactions/',   TransactionListAPIView.as_view(),   name='api_transactions'),
    path('bills/',          BillListAPIView.as_view(),          name='api_bills'),
    path('goals/',          GoalListAPIView.as_view(),          name='api_goals'),

    # ── Plaid banking API ─────────────────────────────────────────────────────
    path('plaid/link-token/',           plaid_views.create_link_token,      name='plaid_link_token'),
    path('plaid/exchange/',             plaid_views.exchange_public_token,  name='plaid_exchange'),
    path('plaid/sync/',                 plaid_views.sync_all,               name='plaid_sync'),
    path('plaid/disconnect/<str:item_id>/', plaid_views.disconnect_institution, name='plaid_disconnect'),
]
