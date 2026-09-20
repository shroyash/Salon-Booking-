import React from 'react';

interface NavbarProps {
  activeTab: 'appointments' | 'services';
  onTabChange: (tab: 'appointments' | 'services') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  return (
    <header className="navbar-header">
      <div className="navbar-container">
        <div className="brand-logo">
          <span className="brand-name">Salon Portal</span>
        </div>
        <nav className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'appointments' ? 'active' : ''}`}
            onClick={() => onTabChange('appointments')}
          >
            Appointments
          </button>
          <button
            className={`nav-tab ${activeTab === 'services' ? 'active' : ''}`}
            onClick={() => onTabChange('services')}
          >
            Services
          </button>
        </nav>
      </div>
    </header>
  );
};
