import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

function Dashboard({ config }) {
  const [stats, setStats] = useState(null);
  const [deployments, setDeployments] = useState([]);

  useEffect(() => {
    fetch('/api/deployments')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setDeployments(data.data.deployments || []);
        }
      })
      .catch(err => console.error('Error:', err));
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
              </tr>
            </thead>
            <tbody>
              {deployments.map(d => (
                <tr key={d.deployment_id}>
                  <td>{d.deployment_id}</td>
                  <td>{d.agent}</td>
                  <td><span className="badge">{d.status}</span></td>
                  <td>{d.successful}/{d.instances}</td>
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
