import { useEffect, useState } from 'react';
import type { OverviewSummary } from '../types';
import { apiFetch } from '../hooks/useApi';

const OverviewPage = () => {
  const [summary, setSummary] = useState<OverviewSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<OverviewSummary>('/api/overview/')
      .then((data) => {
        setSummary(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">WealthWise</p>
          <h1>Financial dashboard</h1>
        </div>
      </header>

      {loading && <p>Loading financial insights...</p>}
      {error && <p className="error-message">{error}</p>}

      {summary && (
        <div className="grid-layout">
          <article className="panel card">
            <h2>Balance</h2>
            <p className="metric">${summary.total_balance.toFixed(2)}</p>
            <p className="detail">{summary.current_month} performance snapshot</p>
          </article>

          <article className="panel card">
            <h2>Upcoming bills</h2>
            <ul>
              {summary.upcoming_bills.map((bill) => (
                <li key={bill.id}>
                  <strong>{bill.name}</strong> • due {bill.due_date}
                </li>
              ))}
            </ul>
          </article>

          <article className="panel card">
            <h2>Recent transactions</h2>
            <ul>
              {summary.recent_transactions.slice(0, 5).map((transaction) => (
                <li key={transaction.id}>
                  {transaction.description} • ${transaction.amount.toFixed(2)}
                </li>
              ))}
            </ul>
          </article>
        </div>
      )}
    </section>
  );
};

export default OverviewPage;
