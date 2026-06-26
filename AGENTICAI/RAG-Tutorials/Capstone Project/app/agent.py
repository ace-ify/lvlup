from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.config import get_settings
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    message: str
    response: str
    model_used: str
    errors: List[str]

@traceable(run_type="llm", name="call_primary_model")
def call_primary_model(state: AgentState) -> Dict[str, Any]:
    """Invoke the primary model (Gemini). Falls back on failure."""
    settings = get_settings()
    logger.info(f"Attempting to invoke primary model: {settings.primary_model}")
    try:
        # Check if key is dummy or empty, if so, we can raise exception early for fallback testing
        if not settings.gemini_api_key or settings.gemini_api_key == "your_google_api_key":
            raise ValueError("Invalid Gemini API key configured.")
            
        llm = ChatGoogleGenerativeAI(
            model=settings.primary_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.7,
            timeout=10.0
        )
        response = llm.invoke(state["message"])
        return {
            "response": str(response.content),
            "model_used": settings.primary_model,
            "errors": state.get("errors", [])
        }
    except Exception as e:
        logger.warning(f"Primary model failed: {e}")
        return {
            "errors": state.get("errors", []) + [str(e)]
        }

@traceable(run_type="llm", name="call_fallback_model")
def call_fallback_model(state: AgentState) -> Dict[str, Any]:
    """Invoke the fallback model (Groq). Falls back on failure."""
    settings = get_settings()
    logger.info(f"Attempting fallback to model: {settings.fallback_model}")
    try:
        if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key":
            raise ValueError("Invalid Groq API key configured.")
            
        llm = ChatGroq(
            model=settings.fallback_model,
            groq_api_key=settings.groq_api_key,
            temperature=0.7,
            timeout=10.0
        )
        response = llm.invoke(state["message"])
        return {
            "response": str(response.content),
            "model_used": settings.fallback_model,
            "errors": state.get("errors", [])
        }
    except Exception as e:
        logger.warning(f"Fallback model failed: {e}")
        return {
            "errors": state.get("errors", []) + [str(e)]
        }

@traceable(name="handle_error")
def handle_error(state: AgentState) -> Dict[str, Any]:
    """Node to handle errors gracefully when all LLMs fail."""
    logger.error(f"Both primary and fallback models failed. Returning graceful error response. Errors: {state.get('errors')}")
    return {
        "response": "I apologize, but I am currently experiencing technical difficulties processing your request. Please try again later.",
        "model_used": "none",
        "errors": state.get("errors", [])
    }

def route_primary(state: AgentState) -> str:
    # If response is set, we succeeded and go to END, else we call fallback
    if state.get("response"):
        return END
    return "call_fallback_model"

def route_fallback(state: AgentState) -> str:
    # If response is set, we succeeded and go to END, else we handle error
    if state.get("response"):
        return END
    return "handle_error"

# Build the LangGraph StateMachine
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("call_primary_model", call_primary_model)
workflow.add_node("call_fallback_model", call_fallback_model)
workflow.add_node("handle_error", handle_error)

# Set Entry Point
workflow.set_entry_point("call_primary_model")

# Add Conditional Edges
workflow.add_conditional_edges(
    "call_primary_model",
    route_primary,
    {
        END: END,
        "call_fallback_model": "call_fallback_model"
    }
)
workflow.add_conditional_edges(
    "call_fallback_model",
    route_fallback,
    {
        END: END,
        "handle_error": "handle_error"
    }
)

# Connect handle_error to END
workflow.add_edge("handle_error", END)

# Compile
compiled_agent = workflow.compile()
