const BASE_URL = 'http://localhost:8000';

/**
 * Sends a design description prompt to the FastAPI backend
 * and returns the generated REST API schema and analysis results.
 * 
 * @param {string} prompt - The project description.
 * @returns {Promise<object>} The generated design response.
 */
export async function generateEndpoints(prompt) {
  const response = await fetch(`${BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      detail: 'An unknown server error occurred.' 
    }));
    throw new Error(errorData.detail || `Server responded with status code ${response.status}`);
  }

  return response.json();
}

/**
 * Sends the current endpoints and a refinement instruction prompt
 * to the FastAPI backend to dynamically update the REST API design.
 * 
 * @param {Array} endpoints - The current endpoints.
 * @param {string} prompt - The modification instruction.
 * @returns {Promise<object>} The updated design response.
 */
export async function refineEndpoints(endpoints, prompt) {
  const response = await fetch(`${BASE_URL}/refine`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ endpoints, prompt }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      detail: 'An unknown server error occurred.' 
    }));
    throw new Error(errorData.detail || `Server responded with status code ${response.status}`);
  }

  return response.json();
}
