// React frontend - App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import DeploymentPanel from './components/DeploymentPanel';
import InstanceList from './components/InstanceList';
import HealthCheckPanel from './components/HealthCheckPanel';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState(null);
  const [deploymentStatus, setDeploymentStatus] = useState(null);

  useEffect(() => {
    // Fetch configuration on mount
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setConfig(data.data);
        }
      })
      .catch(err => console.error('Error fetching config:', err));
  }, []);

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🚀 AWS Security Agent Deployer</h1>
          <p>Deploy Qualys and CrowdStrike agents remotely on AWS EC2 instances</p>
        </div>
      </header>

      <nav className="app-nav">
        <button 
          className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`nav-button ${activeTab === 'instances' ? 'active' : ''}`}
          onClick={() => setActiveTab('instances')}
        >
          💾 Instances
        </button>
        <button 
          className={`nav-button ${activeTab === 'deploy' ? 'active' : ''}`}
          onClick={() => setActiveTab('deploy')}
        >
          ⚡ Deploy
        </button>
        <button 
          className={`nav-button ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          ❤️ Health Check
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard config={config} />}
        {activeTab === 'instances' && <InstanceList />}
        {activeTab === 'deploy' && <DeploymentPanel onStatusChange={setDeploymentStatus} />}
        {activeTab === 'health' && <HealthCheckPanel />}
      </main>

      {deploymentStatus && (
        <div className="deployment-notification">
          <p>{deploymentStatus.message}</p>
          {deploymentStatus.error && <p className="error">{deploymentStatus.error}</p>}
        </div>
      )}

      <footer className="app-footer">
        <p>AWS Security Agent Deployer v1.0.0 | Built with ❤️ for security teams</p>
      </footer>
    </div>
  );
}

export default App;
