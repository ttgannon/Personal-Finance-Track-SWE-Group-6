import { NavLink } from "react-router-dom";

const TopNav = () => (
  <header className="top-nav">
    <div className="brand-group">
      <div className="brand">WealthWise</div>
      <p className="brand-tag">
        A smarter financial workspace for modern earners.
      </p>
    </div>

    <nav className="top-links">
      <NavLink
        to="/"
        end
        className={({ isActive }) => (isActive ? "active" : "")}
      >
        Overview
      </NavLink>
      <NavLink
        to="/accounts"
        className={({ isActive }) => (isActive ? "active" : "")}
      >
        Accounts
      </NavLink>
      <a href="/accounts/logout/" className="logout-link">
        Sign out
      </a>
    </nav>
  </header>
);

export default TopNav;
