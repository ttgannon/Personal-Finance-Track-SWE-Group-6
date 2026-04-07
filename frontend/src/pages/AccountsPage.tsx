import { useEffect, useMemo, useState } from 'react';
import type { BankAccount } from '../types';
import { apiFetch } from '../hooks/useApi';

const AccountsPage = () => {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<BankAccount[]>('/api/accounts/').then((data) => {
      setAccounts(data);
      setLoading(false);
    });
  }, []);

  const totalBalance = useMemo(
    () => accounts.reduce((sum, account) => sum + account.balance, 0),
    [accounts]
  );

  return (
    <section className="dashboard-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Accounts</p>
          <h1>All your institutions in one view</h1>
        </div>
      </header>

      {loading ? (
        <p className="status-message">Loading your accounts…</p>
      ) : (
        <>
          <div className="cards-row">
            <article className="glass-card account-summary-card">
              <p>Linked accounts</p>
              <strong>{accounts.length}</strong>
            </article>
            <article className="glass-card account-summary-card">
              <p>Total available balance</p>
              <strong>${totalBalance.toFixed(2)}</strong>
            </article>
          </div>

          <div className="account-grid">
            {accounts.map((account) => (
              <article key={account.id} className="account-card">
                <div className="account-card-header">
                  <h3>{account.account_name}</h3>
                  <span>{account.account_type}</span>
                </div>
                <p className="account-bank">{account.bank_name}</p>
                <div className="account-details">
                  <span>${account.balance.toFixed(2)}</span>
                  <small>{account.masked_account_number ?? '•••• ••••'}</small>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
};

export default AccountsPage;
