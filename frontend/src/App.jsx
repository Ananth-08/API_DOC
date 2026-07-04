import React, { useState, useEffect } from 'react';
import PromptInput from './components/PromptInput';
import EndpointTable from './components/EndpointTable';
import GapDetector from './components/GapDetector';
import RelationshipGraph from './components/RelationshipGraph';
import { generateEndpoints, refineEndpoints } from './api/client';

// Hand-crafted SVG Icons for professional design
const Icons = {
  Terminal: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
  ),
  Table: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
  ),
  ShieldAlert: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
  ),
  Share2: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.684 10.742l4.632-2.316m0 0a3 3 0 102.684-4.632 3 3 0 00-2.684 4.632zM8.684 13.258l4.632 2.316m0 0a3 3 0 102.684 4.632 3 3 0 00-2.684-4.632zM6.5 12a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" /></svg>
  ),
  Activity: () => (
    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
  )
};

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('generate');
  const [serverOnline, setServerOnline] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const [activeModel, setActiveModel] = useState('gemini-2.5-flash');

  const [refinementInput, setRefinementInput] = useState('');
  const [refining, setRefining] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const handleRefine = async (e) => {
    e.preventDefault();
    if (!refinementInput.trim() || !result) return;

    const userMsg = refinementInput.trim();
    setRefinementInput('');
    setRefining(true);
    setError(null);

    setChatHistory((prev) => [...prev, { sender: 'user', text: userMsg }]);

    try {
      const data = await refineEndpoints(result.endpoints, userMsg);
      setResult(data);
      setChatHistory((prev) => [
        ...prev,
        { sender: 'assistant', text: `Successfully updated the schema! \n\n${data.summary}` }
      ]);
    } catch (err) {
      setError(err.message || 'An error occurred while refining the API design.');
      setChatHistory((prev) => [
        ...prev,
        { sender: 'assistant', text: `❌ Failed to update the schema: ${err.message}` }
      ]);
    } finally {
      setRefining(false);
    }
  };

  // Ping backend to show status in the header
  useEffect(() => {
    fetch('http://localhost:8000/')
      .then((res) => {
        if (res.ok) {
          setServerOnline(true);
          return res.json();
        }
        throw new Error('Offline');
      })
      .then((data) => {
        if (data && data.model) {
          setActiveModel(data.model);
        }
      })
      .catch(() => setServerOnline(false));
  }, []);

  const handleGenerate = async (prompt) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveTab('generate');

    try {
      const data = await generateEndpoints(prompt);
      setResult(data);
      // Auto switch to endpoints view on successful design
      setActiveTab('endpoints');
    } catch (err) {
      setError(err.message || 'An error occurred while generating the API design.');
    } finally {
      setLoading(false);
    }
  };

  // Filter endpoints dynamically if search term is active
  const filteredEndpoints = result?.endpoints?.filter(
    (ep) =>
      ep.route.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ep.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ep.method.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="dashboard-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon"></div>
          <h2>API.DESIGN <span className="logo-accent">AI</span></h2>
        </div>

        <nav className="sidebar-nav">
          <button
            onClick={() => setActiveTab('generate')}
            className={`nav-item ${activeTab === 'generate' ? 'active' : ''}`}
          >
            <Icons.Terminal />
            <span>Generate Design</span>
          </button>

          <button
            onClick={() => result && setActiveTab('endpoints')}
            className={`nav-item ${activeTab === 'endpoints' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
            disabled={!result}
          >
            <Icons.Table />
            <span>Endpoints List</span>
            {result && (
              <span className="badge-count bg-indigo">{result.endpoints.length}</span>
            )}
          </button>

          <button
            onClick={() => result && setActiveTab('linter')}
            className={`nav-item ${activeTab === 'linter' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
            disabled={!result}
          >
            <Icons.ShieldAlert />
            <span>Linter & Gaps</span>
            {result && (result.gaps.length > 0 || result.violations.length > 0) && (
              <span className="badge-count bg-rose">
                {result.gaps.length + result.violations.length}
              </span>
            )}
          </button>

          <button
            onClick={() => result && setActiveTab('graph')}
            className={`nav-item ${activeTab === 'graph' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
            disabled={!result}
          >
            <Icons.Share2 />
            <span>Resource Graph</span>
            {result && result.relationships.length > 0 && (
              <span className="badge-count bg-purple">{result.relationships.length}</span>
            )}
          </button>
        </nav>

        {/* Sidebar Footer Meta */}
        <div className="sidebar-footer">
          <div className="status-indicator">
            <span className={`status-dot ${serverOnline ? 'online' : 'offline'}`}></span>
            <span>FastAPI Backend: {serverOnline ? 'Connected' : 'Offline'}</span>
          </div>
          <div className="model-indicator">
            <span>LLM: {activeModel}</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-viewport">
        {/* Top Navbar */}
        <header className="main-header">
          <div>
            <h1 className="viewport-title">
              {activeTab === 'generate' && 'API Specification Generator'}
              {activeTab === 'endpoints' && 'Designed REST Schema'}
              {activeTab === 'linter' && 'Design Quality Control'}
              {activeTab === 'graph' && 'Entity Relationships'}
            </h1>
            <p className="viewport-subtitle">
              {activeTab === 'generate' && 'Input project specifications to design system architectures.'}
              {activeTab === 'endpoints' && 'Full table of endpoints mapped out by the AI.'}
              {activeTab === 'linter' && 'Overview of REST standard violations and missing CRUD endpoints.'}
              {activeTab === 'graph' && 'Discovered connection models and mappings.'}
            </p>
          </div>

          {/* Search bar inside endpoints view */}
          {activeTab === 'endpoints' && result && (
            <div className="search-wrapper">
              <input
                type="text"
                placeholder="Search endpoints..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          )}
        </header>

        {/* Dynamic Panels */}
        <div className="viewport-content">
          {activeTab === 'generate' && (
            <div className="generate-panel">
              <PromptInput onSubmit={handleGenerate} isLoading={loading} />

              {loading && (
                <div className="loading-container card">
                  <div className="spinner"></div>
                  <h4 className="loading-headline">Consulting AI Architect...</h4>
                  <p className="loading-subtext">Mapping endpoints, running design linter, and identifying relationships.</p>
                </div>
              )}

              {error && (
                <div className="error-message card">
                  <div className="error-icon">⚠</div>
                  <div className="error-details">
                    <h4>Generation Failed</h4>
                    <p>{error}</p>
                    <small>Please verify that your API key is correctly configured in backend/.env</small>
                  </div>
                </div>
              )}

              {result && !loading && (
                <div className="success-overview card">
                  <div className="success-header">
                    <Icons.Activity />
                    <h3>Design Successfully Generated!</h3>
                  </div>
                  <p className="success-description">
                    The schema has been mapped and fully linted. Use the sidebar menu items to explore the details.
                  </p>
                  
                  {/* KPI Summary Block */}
                  <div className="kpi-grid">
                    <div className="kpi-card" onClick={() => setActiveTab('endpoints')}>
                      <span className="kpi-value">{result.endpoints.length}</span>
                      <span className="kpi-label">Endpoints Designed</span>
                    </div>
                    <div className="kpi-card" onClick={() => setActiveTab('linter')}>
                      <span className="kpi-value text-yellow">{result.gaps.length}</span>
                      <span className="kpi-label">Missing CRUD Gaps</span>
                    </div>
                    <div className="kpi-card" onClick={() => setActiveTab('linter')}>
                      <span className="kpi-value text-rose">{result.violations.length}</span>
                      <span className="kpi-label">Lint Violations</span>
                    </div>
                    <div className="kpi-card" onClick={() => setActiveTab('graph')}>
                      <span className="kpi-value text-purple">{result.relationships.length}</span>
                      <span className="kpi-label">Relationships</span>
                    </div>
                  </div>

                  {result.summary && (
                    <div className="summary-block">
                      <h4 className="summary-title">Executive Summary</h4>
                      <p className="summary-text">{result.summary}</p>
                    </div>
                  )}

                  {/* Refinement Chat Section */}
                  <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
                    <h3 className="section-title" style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Iterative Design Refiner</h3>
                    <p className="success-description" style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>Ask the AI to add, modify, or delete endpoints from the current schema.</p>
                    
                    {chatHistory.length > 0 && (
                      <div style={{ background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '1rem', maxHeight: '250px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', border: '1px solid var(--border-color)' }}>
                        {chatHistory.map((chat, idx) => (
                          <div key={idx} style={{ 
                            alignSelf: chat.sender === 'user' ? 'flex-end' : 'flex-start',
                            background: chat.sender === 'user' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                            padding: '0.75rem 1rem',
                            borderRadius: '12px',
                            maxWidth: '85%',
                            fontSize: '0.9rem',
                            border: chat.sender === 'user' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-color)',
                            color: 'white'
                          }}>
                            <strong>{chat.sender === 'user' ? 'You' : 'AI Architect'}:</strong>
                            <p style={{ marginTop: '0.25rem', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>{chat.text}</p>
                          </div>
                        ))}
                        {refining && (
                          <div style={{ alignSelf: 'flex-start', background: 'rgba(255, 255, 255, 0.05)', padding: '0.75rem 1rem', borderRadius: '12px', fontSize: '0.9rem', color: 'var(--color-text-muted)', border: '1px solid var(--border-color)' }}>
                            <span className="spinner-small" style={{ marginRight: '8px', display: 'inline-block', verticalAlign: 'middle' }}></span>
                            Refining schema design...
                          </div>
                        )}
                      </div>
                    )}

                    <form onSubmit={handleRefine} style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="text"
                        placeholder="e.g., Add an admin route to suspend user accounts..."
                        value={refinementInput}
                        onChange={(e) => setRefinementInput(e.target.value)}
                        disabled={refining}
                        style={{
                          flex: 1,
                          background: 'var(--bg-input)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          padding: '0.75rem 1rem',
                          color: 'white',
                          fontFamily: 'var(--font-sans)',
                          fontSize: '0.95rem',
                          outline: 'none',
                        }}
                      />
                      <button 
                        type="submit" 
                        className="btn-primary" 
                        disabled={refining || !refinementInput.trim()}
                        style={{ padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%)', border: 'none', borderRadius: 'var(--radius-sm)', color: 'white', fontWeight: 'bold', cursor: 'pointer' }}
                      >
                        {refining ? 'Refining...' : 'Refine'}
                      </button>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'endpoints' && result && (
            <div className="fade-in">
              <EndpointTable endpoints={filteredEndpoints} />
            </div>
          )}

          {activeTab === 'linter' && result && (
            <div className="fade-in">
              <GapDetector gaps={result.gaps} violations={result.violations} />
            </div>
          )}

          {activeTab === 'graph' && result && (
            <div className="fade-in">
              <RelationshipGraph relationships={result.relationships} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
