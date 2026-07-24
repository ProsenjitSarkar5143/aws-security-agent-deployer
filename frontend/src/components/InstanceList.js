import React, { useState, useEffect } from 'react';
import '../styles/InstanceList.css';

function InstanceList() {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/instances')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setInstances(data.data.instances || []);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="instance-list-container">
      <h2>EC2 Instances</h2>
      {loading ? (
        <p>Loading instances...</p>
      ) : instances.length > 0 ? (
        <div className="instances-grid">
          {instances.map(inst => (
            <div key={inst.instance_id} className="instance-card">
              <div className="card-header">
                <h3>{inst.tags.Name || inst.instance_id}</h3>
                <span className="state-badge">{inst.state}</span>
              </div>
              <div className="card-body">
                <p><strong>Type:</strong> {inst.instance_type}</p>
                <p><strong>Private IP:</strong> {inst.private_ip}</p>
                <p><strong>Public IP:</strong> {inst.public_ip || 'N/A'}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No instances found</p>
      )}
    </div>
  );
}

export default InstanceList;
