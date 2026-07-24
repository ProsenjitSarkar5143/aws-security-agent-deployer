// React component - InstanceList.js
import React, { useState, useEffect } from 'react';
import '../styles/InstanceList.css';

function InstanceList() {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('running');
  const [selectedInstance, setSelectedInstance] = useState(null);

  useEffect(() => {
    fetchInstances();
  }, [filter]);

  const fetchInstances = () => {
    setLoading(true);
    fetch(`/api/instances?state=${filter}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setInstances(data.data.instances || []);
        }
      })
      .catch(err => console.error('Error fetching instances:', err))
      .finally(() => setLoading(false));
  };

  const handleInstanceClick = async (instanceId) => {
    try {
      const response = await fetch(`/api/instances/${instanceId}`);
      const data = await response.json();
      if (data.success) {
        setSelectedInstance(data.data);
      }
    } catch (error) {
      console.error('Error fetching instance details:', error);
    }
  };

  return (
    <div className="instance-list-container">
      <h2>EC2 Instances</h2>
      
      <div className="filter-section">
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="running">Running</option>
          <option value="stopped">Stopped</option>
          <option value="pending">Pending</option>
          <option value="terminated">Terminated</option>
        </select>
        <button onClick={fetchInstances} className="refresh-button">🔄 Refresh</button>
      </div>

      {loading ? (
        <p className="loading">Loading instances...</p>
      ) : instances.length > 0 ? (
        <div className="instances-grid">
          {instances.map(instance => (
            <div 
              key={instance.instance_id} 
              className="instance-card"
              onClick={() => handleInstanceClick(instance.instance_id)}
            >
              <div className="card-header">
                <h3>{instance.tags.Name || instance.instance_id}</h3>
                <span className={`state-badge ${instance.state}`}>{instance.state}</span>
              </div>
              <div className="card-body">
                <p><strong>Instance Type:</strong> {instance.instance_type}</p>
                <p><strong>Private IP:</strong> {instance.private_ip}</p>
                <p><strong>Public IP:</strong> {instance.public_ip || 'N/A'}</p>
                {Object.keys(instance.tags).length > 0 && (
                  <div className="tags">
                    {Object.entries(instance.tags).map(([key, value]) => (
                      <span key={key} className="tag">{key}: {value}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-instances">No instances found</p>
      )}

      {selectedInstance && (
        <div className="instance-details-modal">
          <div className="modal-content">
            <button className="close-button" onClick={() => setSelectedInstance(null)}>×</button>
            <h3>Instance Details</h3>
            <div className="details">
              <p><strong>Instance ID:</strong> {selectedInstance.instance_id}</p>
              <p><strong>Type:</strong> {selectedInstance.instance_type}</p>
              <p><strong>State:</strong> {selectedInstance.instance_state}</p>
              <p><strong>Private IP:</strong> {selectedInstance.private_ip}</p>
              <p><strong>Public IP:</strong> {selectedInstance.public_ip || 'N/A'}</p>
              <p><strong>Launched:</strong> {selectedInstance.launch_time || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default InstanceList;
