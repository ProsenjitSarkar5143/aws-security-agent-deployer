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
      .catch(err => console.error('Error:', err));
  }, []);

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
      console.error('Error:', error);
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
        <button className="health-check-button" onClick={handleHealthCheck} disabled={loading}>
          {loading ? 'Checking...' : '❤️ Run Health Check'}
        </button>
      </div>
      <div className="instances-section">
        <h3>Select Instances ({selectedInstances.length})</h3>
        <div className="instances-list">
          {instances.map(inst => (
            <div key={inst.instance_id} className="instance-item">
              <input type="checkbox" checked={selectedInstances.includes(inst.instance_id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedInstances([...selectedInstances, inst.instance_id]);
                  } else {
                    setSelectedInstances(selectedInstances.filter(id => id !== inst.instance_id));
                  }
                }} />
              <div className="instance-details">
                <p><strong>{inst.tags.Name || inst.instance_id}</strong></p>
                <p>{inst.private_ip}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      {results && (
        <div className={`health-check-result ${results.success ? '' : 'error'}`}>
          <h3>{results.success ? '✅ Check Complete' : '❌ Error'}</h3>
          <p>{results.message}</p>
        </div>
      )}
    </div>
  );
}

export default HealthCheckPanel;
