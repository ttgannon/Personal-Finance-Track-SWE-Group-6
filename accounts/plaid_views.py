"""
Plaid banking API integration for WealthWise.

Flow:
  1. Frontend calls /api/plaid/link-token/  → server returns a short-lived link_token
  2. Frontend opens Plaid Link with that token; user authenticates with their bank
  3. Plaid Link returns a one-time public_token + metadata to the frontend
  4. Frontend calls /api/plaid/exchange/    → server swaps for a permanent access_token,
     stores it in PlaidItem, and immediately syncs accounts + transactions
  5. Ongoing:  /api/plaid/sync/            → re-syncs all linked institutions
  6. Cleanup:  /api/plaid/disconnect/      → removes an institution + its data

Sandbox test credentials (no real bank needed):
  Username: user_good  |  Password: pass_good
"""

import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_remove_request import ItemRemoveRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from .models import BankAccount, Category, PlaidItem, Transaction

logger = logging.getLogger(__name__)


# ── Plaid client factory ──────────────────────────────────────────────────────

def _get_client() -> plaid_api.PlaidApi:
    env_map = {
        'sandbox':     plaid.Environment.Sandbox,
        'development': plaid.Environment.Sandbox,   # plaid-python has no Development env
        'production':  plaid.Environment.Production,
    }
    host = env_map.get(getattr(settings, 'PLAID_ENV', 'sandbox'), plaid.Environment.Sandbox)
    configuration = plaid.Configuration(
        host=host,
        api_key={
            'clientId': getattr(settings, 'PLAID_CLIENT_ID', ''),
            'secret':   getattr(settings, 'PLAID_SECRET', ''),
        }
    )
    return plaid_api.PlaidApi(plaid.ApiClient(configuration))


def _plaid_configured() -> bool:
    return bool(
        getattr(settings, 'PLAID_CLIENT_ID', '') and
        getattr(settings, 'PLAID_SECRET', '')
    )


# ── Plaid category → our Category model ──────────────────────────────────────

_CATEGORY_MAP = {
    'Food and Drink': 'Food',
    'Restaurants':    'Food',
    'Groceries':      'Food',
    'Travel':         'Transportation',
    'Transportation': 'Transportation',
    'Gas Stations':   'Transportation',
    'Entertainment':  'Entertainment',
    'Recreation':     'Entertainment',
    'Arts':           'Entertainment',
    'Shopping':       'Shopping',
    'Shops':          'Shopping',
    'Rent':           'Housing',
    'Mortgage':       'Housing',
    'Housing':        'Housing',
    'Utilities':      'Housing',
}

def _resolve_category(plaid_cats: list) -> Category:
    for name in (plaid_cats or []):
        if name in _CATEGORY_MAP:
            cat, _ = Category.objects.get_or_create(name=_CATEGORY_MAP[name])
            return cat
    cat, _ = Category.objects.get_or_create(name='Others')
    return cat


# ── Internal sync helpers ─────────────────────────────────────────────────────

def _sync_accounts(user, plaid_item: PlaidItem) -> int:
    """Fetch accounts from Plaid and upsert into BankAccount. Returns count."""
    client = _get_client()
    response = client.accounts_get(
        AccountsGetRequest(access_token=plaid_item.access_token)
    )

    _type_map = {
        'depository': 'checking',
        'credit':     'credit',
        'investment': 'investment',
        'loan':       'loan',
    }

    count = 0
    for acct in response['accounts']:
        mask    = acct.get('mask') or '0000'
        balance = acct['balances'].get('current') or 0

        BankAccount.objects.update_or_create(
            user=user,
            plaid_account_id=acct['account_id'],
            defaults={
                'plaid_item_id':  plaid_item.item_id,
                'account_name':   acct.get('name', 'Account'),
                'bank_name':      plaid_item.institution_name,
                'account_number': f'****{mask}',
                'account_type':   _type_map.get(str(acct.get('type', '')), 'checking'),
                'balance':        balance,
                'card_type':      'other',
            }
        )
        count += 1

    return count


def _sync_transactions(user, plaid_item: PlaidItem) -> dict:
    """
    Use Plaid transactions/sync to pull added/modified/removed transactions.
    Returns {'added': n, 'modified': n, 'removed': n}.
    """
    client = _get_client()
    cursor = plaid_item.cursor or ''

    added_list, modified_list, removed_list = [], [], []
    has_more = True

    while has_more:
        kwargs = {'access_token': plaid_item.access_token}
        if cursor:
            kwargs['cursor'] = cursor
        response = client.transactions_sync(TransactionsSyncRequest(**kwargs))
        added_list.extend(response['added'])
        modified_list.extend(response['modified'])
        removed_list.extend(response['removed'])
        has_more = response['has_more']
        cursor   = response['next_cursor']

    plaid_item.cursor = cursor
    plaid_item.save(update_fields=['cursor', 'updated_at'])

    others_cat, _ = Category.objects.get_or_create(name='Others')

    for tx in added_list + modified_list:
        raw_amount = float(tx.get('amount', 0))
        # Plaid: positive amount = money leaving account (expense)
        tx_type = 'expense' if raw_amount >= 0 else 'revenue'
        amount  = abs(raw_amount)

        category = _resolve_category(tx.get('category') or [])

        Transaction.objects.update_or_create(
            user=user,
            plaid_transaction_id=tx['transaction_id'],
            defaults={
                'item_name':       tx.get('name', 'Transaction'),
                'shop_name':       tx.get('merchant_name') or tx.get('name', ''),
                'amount':          amount,
                'date':            tx['date'],
                'transaction_type': tx_type,
                'payment_method':  'credit_card',
                'category':        category,
                'is_deleted':      False,
                'deleted_at':      None,
            }
        )

    for tx in removed_list:
        Transaction.objects.filter(
            user=user, plaid_transaction_id=tx['transaction_id']
        ).update(is_deleted=True)

    return {
        'added':    len(added_list),
        'modified': len(modified_list),
        'removed':  len(removed_list),
    }


# ── API endpoints ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def create_link_token(request):
    """
    Step 1: Create a short-lived Plaid Link token for the frontend.
    The token is tied to this user session and expires in 30 minutes.
    """
    if not _plaid_configured():
        return JsonResponse(
            {'error': 'Plaid is not configured. Add PLAID_CLIENT_ID and PLAID_SECRET to your .env file.'},
            status=503
        )

    try:
        client = _get_client()
        link_request = LinkTokenCreateRequest(
            products=[Products('transactions')],
            client_name='WealthWise',
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id=str(request.user.id)),
        )
        response = client.link_token_create(link_request)
        return JsonResponse({'link_token': response['link_token']})

    except ApiException as exc:
        logger.error('Plaid create_link_token error: %s', exc)
        return JsonResponse({'error': str(exc)}, status=400)
    except Exception as exc:
        logger.exception('Unexpected error in create_link_token')
        return JsonResponse({'error': str(exc)}, status=500)


@login_required
@require_POST
def exchange_public_token(request):
    """
    Step 2: Exchange Plaid's one-time public_token for a permanent access_token.
    Immediately syncs accounts and transactions for the linked institution.
    """
    try:
        body        = json.loads(request.body)
        public_token = body['public_token']
        metadata    = body.get('metadata', {})
        institution = metadata.get('institution', {})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    try:
        client   = _get_client()
        exchange = client.item_public_token_exchange(
            ItemPublicTokenExchangeRequest(public_token=public_token)
        )

        plaid_item, _ = PlaidItem.objects.update_or_create(
            user=request.user,
            item_id=exchange['item_id'],
            defaults={
                'access_token':     exchange['access_token'],
                'institution_id':   institution.get('institution_id', ''),
                'institution_name': institution.get('name', 'Connected Bank'),
            }
        )

        accounts_count = _sync_accounts(request.user, plaid_item)
        tx_stats       = _sync_transactions(request.user, plaid_item)

        return JsonResponse({
            'success':          True,
            'institution':      plaid_item.institution_name,
            'accounts_synced':  accounts_count,
            'transactions':     tx_stats,
        })

    except ApiException as exc:
        logger.error('Plaid exchange_public_token error: %s', exc)
        return JsonResponse({'error': str(exc)}, status=400)
    except Exception as exc:
        logger.exception('Unexpected error in exchange_public_token')
        return JsonResponse({'error': str(exc)}, status=500)


@login_required
@require_POST
def sync_all(request):
    """
    Re-sync all linked institutions: refresh account balances and pull
    any new/modified/removed transactions since the last sync.
    """
    items = PlaidItem.objects.filter(user=request.user)
    if not items.exists():
        return JsonResponse({'error': 'No banks connected.'}, status=400)

    results = []
    for item in items:
        try:
            accounts_count = _sync_accounts(request.user, item)
            tx_stats       = _sync_transactions(request.user, item)
            results.append({
                'institution':     item.institution_name,
                'accounts_synced': accounts_count,
                'transactions':    tx_stats,
                'ok':              True,
            })
        except ApiException as exc:
            results.append({'institution': item.institution_name, 'ok': False, 'error': str(exc)})
        except Exception as exc:
            logger.exception('Error syncing item %s', item.item_id)
            results.append({'institution': item.institution_name, 'ok': False, 'error': str(exc)})

    return JsonResponse({'results': results})


@login_required
@require_POST
def disconnect_institution(request, item_id):
    """
    Remove a linked institution. Deletes the PlaidItem, its BankAccounts,
    and calls Plaid's /item/remove so they stop charging API credits.
    """
    try:
        plaid_item = PlaidItem.objects.get(user=request.user, item_id=item_id)
    except PlaidItem.DoesNotExist:
        return JsonResponse({'error': 'Institution not found.'}, status=404)

    # Best-effort Plaid-side removal (don't fail if Plaid call errors)
    try:
        client = _get_client()
        client.item_remove(ItemRemoveRequest(access_token=plaid_item.access_token))
    except Exception as exc:
        logger.warning('Plaid item_remove failed (still removing locally): %s', exc)

    # Remove all accounts imported from this institution
    BankAccount.objects.filter(user=request.user, plaid_item_id=item_id).delete()

    institution_name = plaid_item.institution_name
    plaid_item.delete()

    return JsonResponse({'success': True, 'institution': institution_name})
