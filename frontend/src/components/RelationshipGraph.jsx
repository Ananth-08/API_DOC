import React from 'react';

export default function RelationshipGraph({ relationships = [] }) {
  if (!relationships || !relationships.length) {
    return (
      <div className="relationship-graph card">
        <h3 className="section-title">Resource Relationships</h3>
        <p className="no-issues">No database or entity relationships detected in the API schema.</p>
      </div>
    );
  }

  return (
    <div className="relationship-graph card">
      <h3 className="section-title">Resource Relationships</h3>
      <div className="relationships-grid">
        {relationships.map((rel, idx) => (
          <div key={idx} className="relationship-card">
            <div className="rel-node rel-parent">{rel.parent}</div>
            <div className="rel-connector">
              <span className="rel-type">{rel.relationship_type}</span>
              <span className="rel-arrow">⟶</span>
            </div>
            <div className="rel-node rel-child">{rel.child}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
