import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from agent import run_agent
from schemas import PromptRequest, GenerateResponse

app = FastAPI(
    title="REST API Schema Generator Service",
    description="A FastAPI backend that generates, analyzes, lints, and structures REST API specifications using LLM agents.",
    version="1.0.0"
)

# Enable Cross-Origin Resource Sharing (CORS) to allow connections from a React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint to verify backend service status and active model.
    """
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    
    llm_provider = os.getenv("LLM_PROVIDER")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not llm_provider:
        if groq_key:
            llm_provider = "groq"
        elif openrouter_key:
            llm_provider = "openrouter"
        else:
            llm_provider = "gemini"
            
    if llm_provider == "groq":
        model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
        provider = "Groq"
    elif llm_provider == "openrouter":
        model_name = os.getenv("OPENROUTER_MODEL_NAME", "meta-llama/llama-3.3-70b-instruct:free")
        provider = "OpenRouter"
    else:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        provider = "Gemini"
        
    return {
        "status": "healthy",
        "service": "REST API Generator Backend",
        "version": "1.0.0",
        "model": f"{provider} ({model_name})"
    }

@app.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_200_OK)
def generate_schema(request: PromptRequest):
    """
    Generates a structured API design using the LangChain agent.
    Runs CRUD gap analysis, REST lint checks, and resource relationship mapping.
    """
    # Additional validation to ensure the prompt is not just whitespace
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The prompt cannot be empty or consist only of whitespace characters."
        )

    try:
        # Call the orchestrator agent
        result = run_agent(prompt)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API schema: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
