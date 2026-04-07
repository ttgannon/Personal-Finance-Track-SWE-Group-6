import { Routes, Route, Navigate } from "react-router-dom";
import OverviewPage from "./pages/OverviewPage";
import AccountsPage from "./pages/AccountsPage";
import TopNav from "./components/TopNav";

function App() {
  return (
    <div className="app-shell">
      <TopNav />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/accounts" element={<AccountsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
