import { useEffect, useState } from "react";
import type { OverviewSummary } from "../types";
import { apiFetch } from "../hooks/useApi";

const OverviewPage = () => {
  const [summary, setSummary] = useState<OverviewSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<OverviewSummary>("/api/overview/")
      .then((data) => {
        setSummary(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const renderChart = () => {
    if (!summary) {
      return null;
    }

    const chartItems = summary.recent_transactions.slice(0, 6);
    const maxAmount = Math.max(1, ...chartItems.map((item) => item.amount));

    return (
      <div className="trend-chart">
        {chartItems.map((item) => (
          <div key={item.id} className="trend-bar">
            <div
              className="trend-fill"
              style={{ height: `${(item.amount / maxAmount) * 100}%` }}
            />
            <span>${item.amount.toFixed(0)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <section className="dashboard-shell">
      <div className="dashboard-top">
        <div className="dashboard-copy">
          <p className="eyebrow">Modern finance</p>
          <h1>Smart money management with clarity and confidence</h1>
          <p>
            WealthWise consolidates your spending, accounts, and upcoming bills
            into a single premium dashboard designed for market-ready
            presentation.
          </p>
        </div>

        <div className="hero-card">
          <span className="hero-label">Available balance</span>
          <strong className="hero-value">
            {summary ? `$${summary.total_balance.toFixed(2)}` : "--"}
          </strong>
          <p className="hero-note">
            {summary ? `${summary.current_month} snapshot` : "Loading data..."}
          </p>
        </div>
      </div>

      {loading && <p className="status-message">Loading financial insights…</p>}
      {error && <p className="error-message">{error}</p>}

      {summary && (
        <>
          <div className="grid-layout dashboard-grid">
            <article className="glass-card summary-card">
              <div className="card-head">
                <h2>Dashboard overview</h2>
                <span className="status-pill">Live</span>
              </div>
              <div className="metric-grid">
                <article className="metric-block">
                  <p>Total balance</p>
                  <strong>${summary.total_balance.toFixed(2)}</strong>
                </article>
                <article className="metric-block">
                  <p>Open bills</p>
                  <strong>{summary.upcoming_bills.length}</strong>
                </article>
                <article className="metric-block">
                  <p>Recent transactions</p>
                  <strong>{summary.recent_transactions.length}</strong>
                </article>
              </div>
            </article>

            <article className="glass-card activity-card">
              <div className="card-head">
                <h2>Recent cash flow</h2>
                <p>Top six transaction values</p>
              </div>
              {renderChart()}
            </article>

            <article className="glass-card bills-card">
              <div className="card-head">
                <h2>Upcoming bills</h2>
                <p>Stay ahead of your next obligations</p>
              </div>
              <ul className="list-group">
                {summary.upcoming_bills.map((bill) => (
                  <li key={bill.id}>
                    <span>{bill.name}</span>
                    <strong>{bill.due_date}</strong>
                  </li>
                ))}
              </ul>
            </article>
          </div>

          <div className="grid-layout data-grid">
            <article className="glass-card table-card">
              <div className="card-head">
                <h2>Latest activity</h2>
                <p>Recent spending and income highlights</p>
              </div>
              <ul className="transaction-list">
                {summary.recent_transactions.map((transaction) => (
                  <li key={transaction.id}>
                    <div>
                      <span>{transaction.description}</span>
                      <small>{transaction.date}</small>
                    </div>
                    <strong>${transaction.amount.toFixed(2)}</strong>
                  </li>
                ))}
              </ul>
            </article>
          </div>
        </>
      )}
    </section>
  );
};

export default OverviewPage;
