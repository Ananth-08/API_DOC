import React from 'react';
import { exportToOpenAPI, exportToPostman } from '../api/exporter';

export default function EndpointTable({ endpoints = [] }) {
  if (!endpoints.length) return null;

  const getMethodBadgeClass = (method) => {
    const m = method.toUpperCase();
    if (m === 'GET') return 'badge badge-get';
    if (m === 'POST') return 'badge badge-post';
    if (m === 'PUT' || m === 'PATCH') return 'badge badge-put';
    if (m === 'DELETE') return 'badge badge-delete';
    return 'badge badge-default';
  };

  const downloadFile = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportOpenAPI = () => {
    const spec = exportToOpenAPI(endpoints);
    downloadFile(spec, 'openapi-spec.json', 'application/json');
  };

  const handleExportPostman = () => {
    const spec = exportToPostman(endpoints);
    downloadFile(spec, 'postman-collection.json', 'application/json');
  };

  return (
    <div className="table-container card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h3 className="section-title" style={{ margin: 0 }}>Designed REST Endpoints</h3>
        <div className="export-actions">
          <button 
            onClick={handleExportOpenAPI} 
            className="btn-primary" 
            style={{ marginRight: '8px', padding: '0.5rem 1rem', fontSize: '0.85rem', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}
          >
            📥 Export OpenAPI Spec
          </button>
          <button 
            onClick={handleExportPostman} 
            className="btn-primary" 
            style={{ padding: '0.5rem 1rem', fontSize: '0.85rem', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}
          >
            📥 Export Postman Collection
          </button>
        </div>
      </div>
      <div className="table-scroll">
        <table className="endpoint-table">
          <thead>
            <tr>
              <th style={{ width: '10%' }}>Method</th>
              <th style={{ width: '35%' }}>Route</th>
              <th style={{ width: '40%' }}>Description</th>
              <th style={{ width: '15%', textAlign: 'center' }}>Auth</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((ep, idx) => (
              <tr key={idx}>
                <td>
                  <span className={getMethodBadgeClass(ep.method)}>
                    {ep.method.toUpperCase()}
                  </span>
                </td>
                <td className="route-cell"><code>{ep.route}</code></td>
                <td>{ep.description}</td>
                <td style={{ textAlign: 'center' }}>
                  <span className={`badge ${ep.auth_required ? 'badge-auth-yes' : 'badge-auth-no'}`}>
                    {ep.auth_required ? 'Required' : 'Public'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
