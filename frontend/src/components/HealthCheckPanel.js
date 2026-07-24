// React component - HealthCheckPanel.js
import React, { useState, useEffect } from 'react';
import '../styles/HealthCheckPanel.css';

function HealthCheckPanel() {
  const [agentType, setAgentType] = useState('qualys');
  const [selectedInstances, setSelectedInstances] = useState([]);
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetch('/api/instances')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setInstances(data.data.instances || []);
        }
      })
      .catch(err => console.error('Error fetching instances:', err));
  }, []);

  const handleInstanceToggle = (instanceId) => {
    setSelectedInstances(prev => 
      prev.includes(instanceId) 
        ? prev.filter(id => id !== instanceId)
        : [...prev, instanceId]
    );
  };

  const handleHealthCheck = async () => {
    if (selectedInstances.length === 0) {
      alert('Please select at least one instance');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/health-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: agentType,
          instance_ids: selectedInstances
        })
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Health check error:', error);
      setResults({
        success: false,
        message: 'Health check failed',
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="health-check-panel">
      <h2>Agent Health Check</h2>
      
      <div className="health-check-form">
        <div className="form-group">
          <label>Agent Type:</label>
          <select value={agentType} onChange={(e) => setAgentType(e.target.value)}>
            <option value="qualys">Qualys Cloud Agent</option>
            <option value="crowdstrike">CrowdStrike Falcon</option>
          </select>
        </div>

        <button 
          className="health-check-button" 
          onClick={handleHealthCheck} 
          disabled={loading || selectedInstances.length === 0}
        >
          {loading ? 'Checking...' : '❤️ Run Health Check'}
        </button>
      </div>

      <div className="instances-section">
        <h3>Select Instances ({selectedInstances.length} selected)</h3>
        <div className="instances-list">
          {instances.length > 0 ? (
            instances.map(instance => (
              <div key={instance.instance_id} className="instance-item">
                <input
                  type="checkbox"
                  checked={selectedInstances.includes(instance.instance_id)}
                  onChange={() => handleInstanceToggle(instance.instance_id)}
                />
                <div className="instance-details">
                  <p><strong>{instance.tags.Name || instance.instance_id}</strong></p>
                  <p>{instance.instance_type} | {instance.private_ip}</p>
                  <p className="state">State: {instance.state}</p>
                </div>
              </div>
            ))
          ) : (
            <p>No instances available</p>
          )}
        </div>
      </div>

      {results && (
        <div className={`health-check-result ${results.success ? 'success' : 'error'}`}>
          <h3>{results.success ? '✅ Health Check Complete' : '❌ Error'}</h3>
          <p>{results.message}</p>
          {results.data && (
            <div className="result-stats">
              <p>Total: {results.data.total_instances}</p>
              <p className="healthy">Healthy: {results.data.healthy}</p>
              <p className="unhealthy">Unhealthy: {results.data.unhealthy}</p>
              {results.data.pending > 0 && <p>Pending: {results.data.pending}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default HealthCheckPanel;
