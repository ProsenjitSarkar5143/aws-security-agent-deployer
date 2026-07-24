import React, { useState } from 'react';
import '../styles/AIAssistant.css';

function AIAssistant() {
  const [activeTab, setActiveTab] = useState('recommendation');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({});

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setResult(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files[0]
    }));
  };

  const getRecommendation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/deployment-recommendation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: formData.agent_type || 'qualys',
          instance_count: parseInt(formData.instance_count) || 1,
          instance_types: (formData.instance_types || 't3.medium').split(',').map(s => s.trim()),
          region: formData.region || 'us-east-1',
          environment: formData.environment || 'production'
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const troubleshoot = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/troubleshoot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: formData.agent_type || 'qualys',
          error_message: formData.error_message || '',
          instance_id: formData.instance_id || '',
          logs: formData.logs || ''
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const generateScript = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/generate-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: formData.agent_type || 'qualys',
          os_type: formData.os_type || 'linux',
          custom_requirements: formData.custom_requirements || ''
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const analyzeHealth = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/health-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          health_check_results: JSON.parse(formData.health_results || '{}'),
          deployment_stats: JSON.parse(formData.deployment_stats || '{}')
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const getSecurity = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/security-recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment_config: JSON.parse(formData.deployment_config || '{}'),
          threat_model: formData.threat_model || 'standard'
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const analyzeDiagram = async () => {
    if (!formData.diagram_image) {
      setResult({ error: 'Please select an image' });
      return;
    }

    setLoading(true);
    const form = new FormData();
    form.append('image', formData.diagram_image);

    try {
      const response = await fetch('/api/ai/analyze-diagram', {
        method: 'POST',
        body: form
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const analyzeLogs = async () => {
    if (!formData.logs_image) {
      setResult({ error: 'Please select an image' });
      return;
    }

    setLoading(true);
    const form = new FormData();
    form.append('image', formData.logs_image);

    try {
      const response = await fetch('/api/ai/analyze-logs', {
        method: 'POST',
        body: form
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const getCompliance = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/compliance-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment_info: JSON.parse(formData.deployment_info || '{}'),
          compliance_requirements: (formData.requirements || '').split(',').map(s => s.trim()).filter(s => s)
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const getCostOptimization = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai/cost-optimization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: JSON.parse(formData.deployment_config || '{}'),
          constraints: JSON.parse(formData.constraints || '{}')
        })
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setResult({ error: data.message });
      }
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  return (
    <div className="ai-assistant">
      <h2>🤖 AI Deployment Assistant</h2>
      
      <div className="ai-tabs">
        <button 
          className={`ai-tab ${activeTab === 'recommendation' ? 'active' : ''}`}
          onClick={() => handleTabChange('recommendation')}
        >
          💡 Recommendation
        </button>
        <button 
          className={`ai-tab ${activeTab === 'troubleshoot' ? 'active' : ''}`}
          onClick={() => handleTabChange('troubleshoot')}
        >
          🔧 Troubleshoot
        </button>
        <button 
          className={`ai-tab ${activeTab === 'script' ? 'active' : ''}`}
          onClick={() => handleTabChange('script')}
        >
          📝 Generate Script
        </button>
        <button 
          className={`ai-tab ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => handleTabChange('health')}
        >
          📊 Health Analysis
        </button>
        <button 
          className={`ai-tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => handleTabChange('security')}
        >
          🔐 Security
        </button>
        <button 
          className={`ai-tab ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => handleTabChange('compliance')}
        >
          ✅ Compliance
        </button>
        <button 
          className={`ai-tab ${activeTab === 'cost' ? 'active' : ''}`}
          onClick={() => handleTabChange('cost')}
        >
          💰 Cost
        </button>
        <button 
          className={`ai-tab ${activeTab === 'vision' ? 'active' : ''}`}
          onClick={() => handleTabChange('vision')}
        >
          🖼️ Vision
        </button>
      </div>

      <div className="ai-content">
        {activeTab === 'recommendation' && (
          <div className="ai-form">
            <h3>Get Deployment Recommendation</h3>
            <div className="form-group">
              <label>Agent Type:</label>
              <select name="agent_type" onChange={handleInputChange}>
                <option value="qualys">Qualys</option>
                <option value="crowdstrike">CrowdStrike</option>
              </select>
            </div>
            <div className="form-group">
              <label>Instance Count:</label>
              <input type="number" name="instance_count" onChange={handleInputChange} placeholder="5" />
            </div>
            <div className="form-group">
              <label>Instance Types (comma-separated):</label>
              <input type="text" name="instance_types" onChange={handleInputChange} placeholder="t3.medium,t3.large" />
            </div>
            <div className="form-group">
              <label>AWS Region:</label>
              <input type="text" name="region" onChange={handleInputChange} placeholder="us-east-1" />
            </div>
            <div className="form-group">
              <label>Environment:</label>
              <select name="environment" onChange={handleInputChange}>
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="development">Development</option>
              </select>
            </div>
            <button onClick={getRecommendation} disabled={loading} className="btn-primary">
              {loading ? '⏳ Generating...' : '💡 Get Recommendation'}
            </button>
          </div>
        )}

        {activeTab === 'troubleshoot' && (
          <div className="ai-form">
            <h3>Troubleshoot Deployment Issues</h3>
            <div className="form-group">
              <label>Agent Type:</label>
              <select name="agent_type" onChange={handleInputChange}>
                <option value="qualys">Qualys</option>
                <option value="crowdstrike">CrowdStrike</option>
              </select>
            </div>
            <div className="form-group">
              <label>Error Message:</label>
              <textarea name="error_message" onChange={handleInputChange} placeholder="Paste error message..." />
            </div>
            <div className="form-group">
              <label>Instance ID:</label>
              <input type="text" name="instance_id" onChange={handleInputChange} placeholder="i-1234567890abcdef0" />
            </div>
            <div className="form-group">
              <label>Logs:</label>
              <textarea name="logs" onChange={handleInputChange} placeholder="Paste relevant logs..." />
            </div>
            <button onClick={troubleshoot} disabled={loading} className="btn-primary">
              {loading ? '⏳ Analyzing...' : '🔧 Get Troubleshooting Guide'}
            </button>
          </div>
        )}

        {activeTab === 'script' && (
          <div className="ai-form">
            <h3>Generate Deployment Script</h3>
            <div className="form-group">
              <label>Agent Type:</label>
              <select name="agent_type" onChange={handleInputChange}>
                <option value="qualys">Qualys</option>
                <option value="crowdstrike">CrowdStrike</option>
              </select>
            </div>
            <div className="form-group">
              <label>OS Type:</label>
              <select name="os_type" onChange={handleInputChange}>
                <option value="linux">Linux</option>
                <option value="windows">Windows</option>
              </select>
            </div>
            <div className="form-group">
              <label>Custom Requirements:</label>
              <textarea name="custom_requirements" onChange={handleInputChange} placeholder="Any specific requirements..." />
            </div>
            <button onClick={generateScript} disabled={loading} className="btn-primary">
              {loading ? '⏳ Generating...' : '📝 Generate Script'}
            </button>
          </div>
        )}

        {activeTab === 'health' && (
          <div className="ai-form">
            <h3>Analyze Deployment Health</h3>
            <div className="form-group">
              <label>Health Check Results (JSON):</label>
              <textarea name="health_results" onChange={handleInputChange} placeholder='{"healthy": 10, "unhealthy": 2}' />
            </div>
            <div className="form-group">
              <label>Deployment Stats (JSON):</label>
              <textarea name="deployment_stats" onChange={handleInputChange} placeholder='{"total": 12, "successful": 11}' />
            </div>
            <button onClick={analyzeHealth} disabled={loading} className="btn-primary">
              {loading ? '⏳ Analyzing...' : '📊 Analyze Health'}
            </button>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="ai-form">
            <h3>Security Recommendations</h3>
            <div className="form-group">
              <label>Threat Model:</label>
              <select name="threat_model" onChange={handleInputChange}>
                <option value="standard">Standard</option>
                <option value="advanced">Advanced</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="form-group">
              <label>Deployment Config (JSON):</label>
              <textarea name="deployment_config" onChange={handleInputChange} placeholder='{"mode": "lambda", "region": "us-east-1"}' />
            </div>
            <button onClick={getSecurity} disabled={loading} className="btn-primary">
              {loading ? '⏳ Generating...' : '🔐 Get Recommendations'}
            </button>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="ai-form">
            <h3>Generate Compliance Report</h3>
            <div className="form-group">
              <label>Deployment Info (JSON):</label>
              <textarea name="deployment_info" onChange={handleInputChange} placeholder='{"agents": ["qualys"], "region": "us-east-1"}' />
            </div>
            <div className="form-group">
              <label>Compliance Requirements (comma-separated):</label>
              <input type="text" name="requirements" onChange={handleInputChange} placeholder="SOC2, HIPAA, PCI-DSS" />
            </div>
            <button onClick={getCompliance} disabled={loading} className="btn-primary">
              {loading ? '⏳ Generating...' : '✅ Generate Report'}
            </button>
          </div>
        )}

        {activeTab === 'cost' && (
          <div className="ai-form">
            <h3>Cost Optimization</h3>
            <div className="form-group">
              <label>Deployment Config (JSON):</label>
              <textarea name="deployment_config" onChange={handleInputChange} placeholder='{"instance_type": "t3.large", "count": 5}' />
            </div>
            <div className="form-group">
              <label>Constraints (JSON):</label>
              <textarea name="constraints" onChange={handleInputChange} placeholder='{"performance": "high", "uptime_sla": 0.99}' />
            </div>
            <button onClick={getCostOptimization} disabled={loading} className="btn-primary">
              {loading ? '⏳ Analyzing...' : '💰 Get Recommendations'}
            </button>
          </div>
        )}

        {activeTab === 'vision' && (
          <div className="ai-form">
            <h3>AI Vision Analysis</h3>
            <div className="form-group">
              <label>Select Analysis Type:</label>
              <select name="vision_type" onChange={handleInputChange}>
                <option value="diagram">Deployment Diagram</option>
                <option value="logs">Log Screenshot</option>
              </select>
            </div>
            <div className="form-group">
              <label>Upload Image:</label>
              <input 
                type="file" 
                name={formData.vision_type === 'logs' ? 'logs_image' : 'diagram_image'}
                onChange={handleFileChange}
                accept="image/*"
              />
            </div>
            <button 
              onClick={formData.vision_type === 'logs' ? analyzeLogs : analyzeDiagram}
              disabled={loading} 
              className="btn-primary"
            >
              {loading ? '⏳ Analyzing...' : '🖼️ Analyze Image'}
            </button>
          </div>
        )}

        {result && (
          <div className="ai-result">
            <h3>AI Response</h3>
            <div className="result-content">
              {result.error ? (
                <p className="error">❌ {result.error}</p>
              ) : (
                <div className="markdown-content">
                  {result.recommendation || result.troubleshooting || result.script || result.analysis || result.recommendations || result.report || result.config?.raw_response || result.config || 'No response'}
                </div>
              )}
            </div>
            {!result.error && (
              <button 
                onClick={() => {
                  const text = result.recommendation || result.troubleshooting || result.script || result.analysis || result.recommendations || result.report || JSON.stringify(result);
                  navigator.clipboard.writeText(text);
                  alert('✅ Copied to clipboard!');
                }} 
                className="copy-button"
              >
                📋 Copy to Clipboard
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AIAssistant;
