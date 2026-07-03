import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Build absolute path to backend/.env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables first
load_dotenv(dotenv_path=ENV_PATH)

# Support both GEMINI_API_KEY and GOOGLE_API_KEY
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key and gemini_key != "dummy_key_for_import_validation":
    os.environ["GOOGLE_API_KEY"] = gemini_key

# Prevent ChatGoogleGenerativeAI initialization from failing if key is missing during imports
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "dummy_key_for_import_validation"

from langchain_google_genai import ChatGoogleGenerativeAI

# Attempt to load standard LangChain imports, otherwise fallback to the custom platform build
try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.tools import Tool
    HAS_STANDARD_LANGCHAIN = True
except ImportError:
    # Custom/mock platform LangChain 1.3.11 compatibility
    from langchain.agents import create_agent
    from langchain_core.tools import Tool
    from langchain_core.messages import HumanMessage
    
    class AgentType:
        ZERO_SHOT_REACT_DESCRIPTION = "zero-shot-react-description"
        
    HAS_STANDARD_LANGCHAIN = False

# Import our custom tools logic
from tools.crud_detector import detect_crud_gaps
from tools.linter import lint_endpoints
from tools.relationship_graph import detect_relationships

# Cache to hold initialized LLM and its config
_llm_cache = {}

def get_llm():
    # Reload environment variables from .env to pick up any runtime edits using absolute path
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    
    # Support both GEMINI_API_KEY and GOOGLE_API_KEY
    if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
        
    llm_provider = os.getenv("LLM_PROVIDER")
    
    # Values from env
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_model = os.getenv("OPENROUTER_MODEL_NAME", "google/gemini-2.5-flash")
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    
    gemini_model = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    # Determine provider dynamically if not explicitly specified
    if not llm_provider:
        if groq_api_key:
            llm_provider = "groq"
        elif openrouter_api_key:
            llm_provider = "openrouter"
        else:
            llm_provider = "gemini"
            
    # Cache key based on all parameters
    cache_key = (llm_provider, openrouter_api_key, openrouter_model, groq_api_key, groq_model, gemini_model, google_api_key)
    
    if "llm" in _llm_cache and _llm_cache.get("key") == cache_key:
        return _llm_cache["llm"]
        
    # Re-initialize
    if llm_provider == "groq" and groq_api_key:
        from langchain_groq import ChatGroq
        print(f"Initializing Groq LLM with model: {groq_model}")
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=groq_model,
            temperature=0.0
        )
    elif llm_provider == "openrouter" and openrouter_api_key:
        from langchain_openai import ChatOpenAI
        print(f"Initializing OpenRouter LLM with model: {openrouter_model}")
        llm = ChatOpenAI(
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model=openrouter_model,
            temperature=0.0,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI REST API Designer"
            }
        )
    else:
        # Default fallback to standard Gemini
        effective_key = google_api_key or "dummy_key_for_import_validation"
        from langchain_google_genai import ChatGoogleGenerativeAI
        print(f"Initializing standard Gemini LLM with model: {gemini_model}")
        llm = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=0.0,
            google_api_key=effective_key
        )
        
    _llm_cache["llm"] = llm
    _llm_cache["key"] = cache_key
    return llm

# ----------------- Tool Wrappers -----------------

def run_crud_gap_detector(endpoints_json: str) -> str:
    """Wrapper for detect_crud_gaps that parses JSON input and returns JSON output."""
    try:
        data = json.loads(endpoints_json)
        if isinstance(data, dict):
            if "endpoints" in data:
                data = data["endpoints"]
            elif "input" in data:
                data = json.loads(data["input"])
        
        if not isinstance(data, list):
            return json.dumps({"error": "Input must be a JSON array of endpoints"})
            
        result = detect_crud_gaps(data)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to detect CRUD gaps: {str(e)}"})

def run_rest_linter(endpoints_json: str) -> str:
    """Wrapper for lint_endpoints that parses JSON input and returns JSON output."""
    try:
        data = json.loads(endpoints_json)
        if isinstance(data, dict):
            if "endpoints" in data:
                data = data["endpoints"]
            elif "input" in data:
                data = json.loads(data["input"])
                
        if not isinstance(data, list):
            return json.dumps({"error": "Input must be a JSON array of endpoints"})
            
        result = lint_endpoints(data)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to lint endpoints: {str(e)}"})

def run_relationship_detector(endpoints_json: str) -> str:
    """Wrapper for detect_relationships that parses JSON input and returns JSON output."""
    try:
        data = json.loads(endpoints_json)
        if isinstance(data, dict):
            if "endpoints" in data:
                data = data["endpoints"]
            elif "input" in data:
                data = json.loads(data["input"])
                
        if not isinstance(data, list):
            return json.dumps({"error": "Input must be a JSON array of endpoints"})
            
        result = detect_relationships(data)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to detect relationships: {str(e)}"})

# ----------------- Create Tools List -----------------

tools = [
    Tool(
        name="crud_gap_detector",
        description=(
            "Detects missing CRUD endpoints. "
            "Input must be a valid JSON array of endpoint dicts, each with 'method' and 'route'."
        ),
        func=run_crud_gap_detector
    ),
    Tool(
        name="rest_linter",
        description=(
            "Checks REST convention violations. "
            "Input must be a valid JSON array of endpoint dicts, each with 'method', 'route', and optional 'description'."
        ),
        func=run_rest_linter
    ),
    Tool(
        name="relationship_detector",
        description=(
            "Detects resource relationships. "
            "Input must be a valid JSON array of endpoint dicts, each with 'route'."
        ),
        func=run_relationship_detector
    )
]

# ----------------- Create Agent -----------------

if HAS_STANDARD_LANGCHAIN:
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=5
    )
else:
    # Custom fallback executor using the platform's graph-based create_agent
    class LangGraphAgentExecutor:
        def __init__(self, tools, llm):
            self.agent_graph = create_agent(
                model=llm,
                tools=tools,
                system_prompt=(
                    "You are a REST API designer. Generate endpoints, run your analysis tools on them "
                    "in sequence (crud_gap_detector, rest_linter, relationship_detector), and output "
                    "a combined structured JSON report matching the requested format."
                )
            )
            
        def run(self, prompt: str) -> str:
            print(f"LangGraphAgentExecutor: invoking agent with prompt length: {len(prompt)}")
            result = self.agent_graph.invoke({"messages": [HumanMessage(content=prompt)]})
            print(f"LangGraphAgentExecutor: result type: {type(result)}")
            if isinstance(result, dict):
                print(f"LangGraphAgentExecutor: result keys: {list(result.keys())}")
            messages = result.get("messages", [])
            print(f"LangGraphAgentExecutor: messages count: {len(messages)}")
            for idx, msg in enumerate(messages):
                print(f"  Message {idx}: type={type(msg)}, content_type={type(msg.content)}")
                content_str = str(msg.content)
                print(f"    Content sample: {content_str[:150]}")
            if messages:
                content = messages[-1].content
                if isinstance(content, list):
                    parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            parts.append(part["text"])
                        elif isinstance(part, str):
                            parts.append(part)
                    return "".join(parts)
                return str(content)
            return ""
            
    # Static initialization is removed in favor of dynamic runtime initialization

# ----------------- Orchestration Function -----------------

FALLBACK_OPENROUTER_MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
    "google/gemma-4-31b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free"
]

last_successful_model = "OpenRouter (meta-llama/llama-3.3-70b-instruct:free)"

def get_last_successful_model():
    global last_successful_model
    return last_successful_model

def invoke_with_fallback(prompt: str) -> str:
    # Reload environment variables from .env to pick up any runtime edits using absolute path
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    
    # Clean up and sync Gemini/Google keys
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key != "dummy_key_for_import_validation":
        os.environ["GOOGLE_API_KEY"] = gemini_key

    llm_provider = os.getenv("LLM_PROVIDER", "openrouter").strip().lower()
    
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key == "dummy_key_for_import_validation":
        google_api_key = None

    # Construct attempts list: list of (provider, model_name, api_key)
    attempts = []
    
    # 1. Build models list for each provider
    or_models = []
    if openrouter_api_key:
        primary_or = os.getenv("OPENROUTER_MODEL_NAME")
        if primary_or:
            or_models.append(primary_or)
        for m in FALLBACK_OPENROUTER_MODELS:
            if m not in or_models:
                or_models.append(m)
                
    gemini_models = []
    if google_api_key:
        primary_gemini = os.getenv("GEMINI_MODEL_NAME")
        if primary_gemini:
            gemini_models.append(primary_gemini)
        for m in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
            if m not in gemini_models:
                gemini_models.append(m)
                
    groq_models = []
    if groq_api_key:
        primary_groq = os.getenv("GROQ_MODEL_NAME")
        if primary_groq:
            groq_models.append(primary_groq)
        for m in ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama3-8b-8192"]:
            if m not in groq_models:
                groq_models.append(m)

    # Determine provider priority order
    provider_priority = []
    if llm_provider in ["openrouter", "gemini", "groq"]:
        provider_priority.append(llm_provider)
    for p in ["openrouter", "gemini", "groq"]:
        if p not in provider_priority:
            provider_priority.append(p)
            
    # Add attempts in order of provider priority
    for p in provider_priority:
        if p == "openrouter" and openrouter_api_key:
            for model in or_models:
                attempts.append(("openrouter", model, openrouter_api_key))
        elif p == "gemini" and google_api_key:
            for model in gemini_models:
                attempts.append(("gemini", model, google_api_key))
        elif p == "groq" and groq_api_key:
            for model in groq_models:
                attempts.append(("groq", model, groq_api_key))
                
    if not attempts:
        # Fallback to dummy Gemini model if absolutely no keys are set
        attempts.append(("gemini", os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"), "dummy_key_for_import_validation"))

    last_err = None
    for provider, model_name, api_key in attempts:
        try:
            if provider == "openrouter":
                from langchain_openai import ChatOpenAI
                print(f"invoke_with_fallback: trying OpenRouter model {model_name}")
                llm = ChatOpenAI(
                    openai_api_key=api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    model=model_name,
                    temperature=0.0,
                    default_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "AI REST API Designer"
                    }
                )
            elif provider == "groq":
                from langchain_groq import ChatGroq
                print(f"invoke_with_fallback: trying Groq model {model_name}")
                llm = ChatGroq(
                    groq_api_key=api_key,
                    model_name=model_name,
                    temperature=0.0
                )
            else: # gemini
                from langchain_google_genai import ChatGoogleGenerativeAI
                print(f"invoke_with_fallback: trying Gemini model {model_name}")
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.0,
                    google_api_key=api_key
                )
                
            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content if hasattr(response, "content") else str(response)
            
            global last_successful_model
            last_successful_model = f"{provider.capitalize()} ({model_name})"
            return response_text
        except Exception as e:
            print(f"invoke_with_fallback: failed with {provider} ({model_name}): {str(e)}")
            last_err = e
            continue
            
    raise last_err or ValueError("Failed to execute prompt with all fallback models.")
            
    raise last_err or ValueError("Failed to execute prompt with all fallback models.")

def run_agent(user_prompt: str) -> dict:
    """
    Bypasses the multi-step agent loop and generates the schema using exactly 
    two LLM calls (generation and summary) with local python tools execution.
    """
    # 1. First LLM Call: Generate raw list of REST endpoints
    generation_prompt = f"""You are an expert REST API designer.
Analyze the user requirement and generate a clean list of REST endpoints that satisfy it.

User prompt: "{user_prompt}"

To satisfy this, return ONLY a valid JSON array of dictionaries, where each dictionary has exactly:
- "method": HTTP method in uppercase (GET, POST, PUT, DELETE, PATCH, etc.)
- "route": Route path starting with a forward slash (e.g. /users/{{id}})
- "description": A string description of what the endpoint does
- "auth_required": A boolean value (true or false) indicating if authentication/authorization is required to access the endpoint

Your response must contain ONLY the raw JSON array.
Do not include any explanations, markdown boxes, or extra text.
"""
    
    response_text = invoke_with_fallback(generation_prompt)
    
    if isinstance(response_text, list):
        parts = []
        for part in response_text:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        response_text = "".join(parts)
    elif not isinstance(response_text, str):
        response_text = str(response_text)
        
    # Extract and parse the generated endpoints
    try:
        endpoints = extract_json(response_text)
    except Exception as e:
        endpoints = []
        
    if not isinstance(endpoints, list):
        if isinstance(endpoints, dict) and "endpoints" in endpoints:
            endpoints = endpoints["endpoints"]
        else:
            endpoints = []

    # 2. Deterministic Local Processing using Python tools
    gaps = detect_crud_gaps(endpoints)
    violations = lint_endpoints(endpoints)
    relationships = detect_relationships(endpoints)
    
    # 3. Second LLM Call: Generate a summary of the designed API and verification results
    endpoints_json = json.dumps(endpoints, indent=2)
    gaps_json = json.dumps(gaps, indent=2)
    violations_json = json.dumps(violations, indent=2)
    relationships_json = json.dumps(relationships, indent=2)
    
    summary_prompt = f"""You are an expert REST API designer.
Generate a concise high-level text summary of the following API design and verification results:

Endpoints:
{endpoints_json}

Identified CRUD Gaps:
{gaps_json}

REST Lint Violations:
{violations_json}

Resource Relationships:
{relationships_json}

Summarize what resources are defined, how they relate, and mention any gaps or lint violations found.
"""
    
    try:
        summary = invoke_with_fallback(summary_prompt)
    except Exception as e:
        summary = f"API specification generated successfully. (Failed to generate summary: {str(e)})"
        
    if not isinstance(summary, str):
        summary = str(summary)
        
    # 4. Build final result dictionary
    result_dict = {
        "endpoints": endpoints,
        "gaps": gaps,
        "violations": violations,
        "relationships": relationships,
        "summary": summary
    }

    # Post-process to ensure all required fields are present and correctly typed
    if isinstance(result_dict, dict):
        if "endpoints" in result_dict and isinstance(result_dict["endpoints"], list):
            for ep in result_dict["endpoints"]:
                if isinstance(ep, dict):
                    if "auth_required" not in ep:
                        # Infer auth_required based on description or path, or default to false
                        desc_lower = ep.get("description", "").lower()
                        route_lower = ep.get("route", "").lower()
                        if any(x in route_lower or x in desc_lower for x in ["admin", "secure", "auth", "private", "me", "profile"]):
                            ep["auth_required"] = True
                        else:
                            ep["auth_required"] = False
                    else:
                        ep["auth_required"] = bool(ep["auth_required"])
                        
        # Ensure gaps, violations, relationships, and summary are present to prevent validation issues
        if "gaps" not in result_dict or not isinstance(result_dict["gaps"], list):
            result_dict["gaps"] = []
        else:
            for gap in result_dict["gaps"]:
                if isinstance(gap, dict):
                    if "method" not in gap: gap["method"] = "GET"
                    if "route" not in gap: gap["route"] = "/"
                    if "reason" not in gap: gap["reason"] = "Missing CRUD operation"

        if "violations" not in result_dict or not isinstance(result_dict["violations"], list):
            result_dict["violations"] = []
        else:
            for viol in result_dict["violations"]:
                if isinstance(viol, dict):
                    if "route" not in viol: viol["route"] = "/"
                    if "method" not in viol: viol["method"] = "GET"
                    if "violation" not in viol: viol["violation"] = "Rest violation"
                    if "suggestion" not in viol: viol["suggestion"] = "Fix REST naming"

        if "relationships" not in result_dict or not isinstance(result_dict["relationships"], list):
            result_dict["relationships"] = []
        else:
            for rel in result_dict["relationships"]:
                if isinstance(rel, dict):
                    if "parent" not in rel: rel["parent"] = "resource"
                    if "child" not in rel: rel["child"] = "subresource"
                    if "relationship_type" not in rel: rel["relationship_type"] = "one-to-many"

        if "summary" not in result_dict or not isinstance(result_dict["summary"], str):
            result_dict["summary"] = "API specification generated successfully."

    return result_dict

def extract_json(text: str) -> any:
    """Helper to extract a JSON block (object or array) from the agent's output."""
    text_clean = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text_clean)
    except json.JSONDecodeError:
        pass
        
    # Search for markdown json block
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # Search for first outer brackets or braces
    match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    raise ValueError(f"Could not extract a valid JSON structure from agent response:\n{text}")
            
    raise ValueError(f"Could not extract a valid JSON structure from agent response:\n{text}")


if __name__ == "__main__":
    import sys
    print("Agent file loaded successfully.")
    print(f"Agent Framework Mode: {'Standard LangChain' if HAS_STANDARD_LANGCHAIN else 'Custom LangGraph Fallback'}")
    if len(sys.argv) > 1 and sys.argv[1] == "--test-run":
        # Reload env to ensure we have latest config
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        
        # Check if we have at least one valid API key configured
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        google_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        # Remove dummy api key if it was set during imports and we actually have openrouter/groq
        if google_api_key == "dummy_key_for_import_validation":
            google_api_key = None
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
                
        if not (google_api_key or openrouter_api_key or groq_api_key):
            print("Error: No LLM configuration found. Please set GEMINI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY in backend/.env.")
            sys.exit(1)
        test_prompt = "Create a system for booking flights and checking user profiles."
        print(f"Running test with prompt: '{test_prompt}'")
        try:
            res = run_agent(test_prompt)
            print("\nResult:")
            print(json.dumps(res, indent=2))
        except Exception as err:
            print(f"Error during agent execution: {err}")
