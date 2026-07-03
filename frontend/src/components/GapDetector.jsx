import React from 'react';

export default function GapDetector({ gaps = [], violations = [] }) {
  const hasGaps = gaps && gaps.length > 0;
  const hasViolations = violations && violations.length > 0;

  if (!hasGaps && !hasViolations) {
    return (
      <div className="gap-detector card status-clean">
        <h3 className="section-title">Analysis & Linting</h3>
        <p className="clean-message">✓ No missing CRUD operations or REST design violations detected! High-quality design.</p>
      </div>
    );
  }

  return (
    <div className="gap-detector card">
      <h3 className="section-title">Design Gaps & Linting</h3>
      
      {/* Gaps Section */}
      <div className="analysis-section">
        <h4 className="subsection-title">Missing CRUD Operations ({gaps.length})</h4>
        {hasGaps ? (
          <ul className="violation-list">
            {gaps.map((gap, idx) => (
              <li key={`gap-${idx}`} className="violation-item warn-card">
                <div className="violation-header">
                  <span className="badge-method">{gap.method}</span>
                  <code className="violation-route">{gap.route}</code>
                </div>
                <div className="violation-body">
                  <strong>Issue:</strong> {gap.reason}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-issues">✓ All expected standard CRUD operations are implemented.</p>
        )}
      </div>

      {/* Violations Section */}
      <div className="analysis-section" style={{ marginTop: '2rem' }}>
        <h4 className="subsection-title">REST API Violations ({violations.length})</h4>
        {hasViolations ? (
          <ul className="violation-list">
            {violations.map((v, idx) => (
              <li key={`violation-${idx}`} className="violation-item error-card">
                <div className="violation-header">
                  <span className="badge-method">{v.method || 'ROUTE'}</span>
                  <code className="violation-route">{v.route}</code>
                </div>
                <div className="violation-body">
                  <div className="v-desc"><strong>Violation:</strong> {v.violation}</div>
                  <div className="v-sugg"><strong>Suggestion:</strong> {v.suggestion}</div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-issues">✓ No REST design guidelines violated.</p>
        )}
      </div>
    </div>
  );
}
