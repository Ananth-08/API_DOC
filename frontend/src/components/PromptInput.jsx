import React, { useState } from 'react';

export default function PromptInput({ onSubmit, isLoading }) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) {
      onSubmit(prompt.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-form card">
      <div className="form-group">
        <label htmlFor="prompt-input" className="form-label">
          Describe the application you want to design:
        </label>
        <textarea
          id="prompt-input"
          className="prompt-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., A library management system where users can view books, checkout materials, and admins can manage members and books."
          disabled={isLoading}
          required
        />
      </div>
      <button type="submit" className="btn-primary" disabled={isLoading || !prompt.trim()}>
        {isLoading ? (
          <>
            <span className="spinner-small"></span>
            Generating Schema...
          </>
        ) : (
          'Generate API Design'
        )}
      </button>
    </form>
  );
}
