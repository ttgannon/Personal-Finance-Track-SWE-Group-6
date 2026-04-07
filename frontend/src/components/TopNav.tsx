import { NavLink } from 'react-router-dom';

const TopNav = () => (
  <header className="top-nav">
    <div className="brand">WealthWise</div>
    <nav>
      <NavLink to="/" end>
        Overview
      </NavLink>
      <NavLink to="/accounts">Accounts</NavLink>
    </nav>
  </header>
);

export default TopNav;
