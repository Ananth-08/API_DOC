import React from 'react';

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

  return (
    <div className="table-container card">
      <h3 className="section-title">Designed REST Endpoints</h3>
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
