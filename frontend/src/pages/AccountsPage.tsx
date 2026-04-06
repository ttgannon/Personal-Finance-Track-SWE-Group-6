import { useEffect, useState } from 'react';
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

  return (
    <section className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Accounts</p>
          <h1>Your linked bank accounts</h1>
        </div>
      </header>

      {loading ? (
        <p>Loading accounts…</p>
      ) : (
        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Bank</th>
                <th>Balance</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map((account) => (
                <tr key={account.id}>
                  <td>{account.account_name}</td>
                  <td>{account.account_type}</td>
                  <td>{account.bank_name}</td>
                  <td>${account.balance.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};

export default AccountsPage;
