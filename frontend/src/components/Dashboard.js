// React component - Dashboard.js
import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

function Dashboard({ config }) {
  const [stats, setStats] = useState(null);
  const [deployments, setDeployments] = useState([]);

  useEffect(() => {
    // Fetch deployments history
    fetch('/api/deployments')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setDeployments(data.data.deployments || []);
          
          // Calculate stats
          const totalInstances = data.data.deployments.reduce((sum, d) => sum + d.instances, 0);
          const totalSuccessful = data.data.deployments.reduce((sum, d) => sum + d.successful, 0);
          const totalFailed = data.data.deployments.reduce((sum, d) => sum + d.failed, 0);
          
          setStats({
            totalDeployments: data.data.deployments.length,
            totalInstances,
            totalSuccessful,
            totalFailed,
            successRate: totalInstances > 0 ? ((totalSuccessful / totalInstances) * 100).toFixed(2) : 0
          });
        }
      })
      .catch(err => console.error('Error fetching deployments:', err));
  }, []);

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      
      {config && (
        <div className="config-info">
          <h3>Configuration</h3>
          <div className="config-grid">
            <div className="config-item">
              <label>AWS Region:</label>
              <span>{config.aws_region}</span>
            </div>
            <div className="config-item">
              <label>Deployment Mode:</label>
              <span>{config.deployment_mode}</span>
            </div>
            <div className="config-item">
              <label>Max Concurrent:</label>
              <span>{config.max_concurrent}</span>
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="stats-container">
          <div className="stat-card">
            <h3>Total Deployments</h3>
            <p className="stat-value">{stats.totalDeployments}</p>
          </div>
          <div className="stat-card">
            <h3>Total Instances</h3>
            <p className="stat-value">{stats.totalInstances}</p>
          </div>
          <div className="stat-card success">
            <h3>Successful</h3>
            <p className="stat-value">{stats.totalSuccessful}</p>
          </div>
          <div className="stat-card error">
            <h3>Failed</h3>
            <p className="stat-value">{stats.totalFailed}</p>
          </div>
          <div className="stat-card">
            <h3>Success Rate</h3>
            <p className="stat-value">{stats.successRate}%</p>
          </div>
        </div>
      )}

      <div className="deployments-history">
        <h3>Recent Deployments</h3>
        {deployments.length > 0 ? (
          <table className="deployments-table">
            <thead>
              <tr>
                <th>Deployment ID</th>
                <th>Agent</th>
                <th>Status</th>
                <th>Instances</th>
                <th>Success/Failed</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {deployments.map(deployment => (
                <tr key={deployment.deployment_id}>
                  <td>{deployment.deployment_id}</td>
                  <td>{deployment.agent}</td>
                  <td><span className={`badge ${deployment.status}`}>{deployment.status}</span></td>
                  <td>{deployment.instances}</td>
                  <td>{deployment.successful}/{deployment.failed}</td>
                  <td>{deployment.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No deployments yet</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
