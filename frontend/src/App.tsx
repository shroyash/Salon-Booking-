import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { AppointmentsPage } from './features/appointments/pages/AppointmentsPage';
import { ServicesPage } from './features/services/pages/ServicesPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'appointments' | 'services'>('appointments');

  return (
    <div className="min-h-screen">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <main>
        {activeTab === 'appointments' ? <AppointmentsPage /> : <ServicesPage />}
      </main>
    </div>
  );
};

export default App;
