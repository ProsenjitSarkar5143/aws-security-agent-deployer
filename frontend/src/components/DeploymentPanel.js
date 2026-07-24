import React, { useState, useEffect } from 'react';
import '../styles/DeploymentPanel.css';

function DeploymentPanel({ onStatusChange }) {
  const [agentType, setAgentType] = useState('qualys');
  const [selectedInstances, setSelectedInstances] = useState([]);
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

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

  const handleDeploy = async () => {
    if (selectedInstances.length === 0) {
      alert('Please select at least one instance');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: agentType,
          instance_ids: selectedInstances,
          dry_run: false
        })
      });
      const data = await response.json();
      setResult(data);
      onStatusChange({ message: data.message });
    } catch (error) {
      onStatusChange({ message: 'Deployment failed', error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="deployment-panel">
      <h2>Deploy Security Agent</h2>
      <div className="deployment-form">
        <div className="form-group">
          <label>Agent Type:</label>
          <select value={agentType} onChange={(e) => setAgentType(e.target.value)}>
            <option value="qualys">Qualys Cloud Agent</option>
            <option value="crowdstrike">CrowdStrike Falcon</option>
          </select>
        </div>
        <button className="deploy-button" onClick={handleDeploy} disabled={loading}>
          {loading ? 'Deploying...' : '🚀 Deploy'}
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
      {result && (
        <div className={`deployment-result ${result.success ? '' : 'error'}`}>
          <h3>{result.success ? '✅ Success' : '❌ Error'}</h3>
          <p>{result.message}</p>
        </div>
      )}
    </div>
  );
}

export default DeploymentPanel;
