// React component - DeploymentPanel.js
import React, { useState, useEffect } from 'react';
import '../styles/DeploymentPanel.css';

function DeploymentPanel({ onStatusChange }) {
  const [agentType, setAgentType] = useState('qualys');
  const [deploymentMode, setDeploymentMode] = useState('lambda');
  const [selectedInstances, setSelectedInstances] = useState([]);
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dryRun, setDryRun] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    // Fetch instances
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
          deployment_mode: deploymentMode,
          dry_run: dryRun
        })
      });

      const data = await response.json();
      setResult(data);
      onStatusChange({
        message: data.message,
        error: !data.success ? data.message : null
      });
    } catch (error) {
      console.error('Deployment error:', error);
      onStatusChange({
        message: 'Deployment failed',
        error: error.message
      });
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

        <div className="form-group">
          <label>Deployment Mode:</label>
          <select value={deploymentMode} onChange={(e) => setDeploymentMode(e.target.value)}>
            <option value="lambda">Lambda (Serverless)</option>
            <option value="ec2">EC2 (On-Demand)</option>
          </select>
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={dryRun} 
              onChange={(e) => setDryRun(e.target.checked)}
            />
            Dry Run (Test without actual deployment)
          </label>
        </div>

        <button 
          className="deploy-button" 
          onClick={handleDeploy} 
          disabled={loading || selectedInstances.length === 0}
        >
          {loading ? 'Deploying...' : '🚀 Deploy'}
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

      {result && (
        <div className={`deployment-result ${result.success ? 'success' : 'error'}`}>
          <h3>{result.success ? '✅ Success' : '❌ Error'}</h3>
          <p>{result.message}</p>
          {result.data && result.data.successful !== undefined && (
            <div className="result-stats">
              <p>Successful: {result.data.successful}</p>
              <p>Failed: {result.data.failed}</p>
              <p>Total: {result.data.total_instances}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DeploymentPanel;
