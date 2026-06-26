from typing import Annotated, Optional, Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.config import get_settings
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    error: Optional[str]
    retry_count: int
    model_used: str

class ProductionAgent:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.graph = self._build_graph()

    def _build_graph(self):
        def process_message(state: AgentState) -> dict:
            settings = get_settings()
            logger.info(f"Attempting to invoke primary model: {settings.primary_model}")
            try:
                if not settings.gemini_api_key or settings.gemini_api_key == "your_google_api_key":
                    raise ValueError("Invalid Gemini API key configured.")
                
                llm = ChatGoogleGenerativeAI(
                    model=settings.primary_model,
                    google_api_key=settings.gemini_api_key,
                    temperature=0.7,
                    timeout=10.0
                )
                response = llm.invoke(state["messages"])
                return {
                    "messages": [response],
                    "model_used": settings.primary_model,
                    "error": None
                }
            except Exception as e:
                logger.warning(f"Primary model failed: {e}")
                return {
                    "error": str(e),
                    "retry_count": state.get("retry_count", 0) + 1
                }

        def try_fallback(state: AgentState) -> dict:
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
                response = llm.invoke(state["messages"])
                return {
                    "messages": [response],
                    "model_used": settings.fallback_model,
                    "error": None
                }
            except Exception as e:
                logger.warning(f"Fallback model failed: {e}")
                return {
                    "error": str(e)
                }

        def handle_error(state: AgentState) -> dict:
            """Return a graceful error message."""
            return {
                "messages": [
                    AIMessage(content=(
                        "I'm sorry, I'm having trouble processing your request "
                        "right now. Please try again in a moment."
                    ))
                ],
                "model_used": "error_handler",
            }

        def route_after_process(state: AgentState) -> str:
            """Decide what to do after primary model attempt."""
            if state.get("error") is None:
                return "done"
            elif state["retry_count"] < self.max_retries:
                return "fallback"
            else:
                return "error"

        def route_after_fallback(state: AgentState) -> str:
            """Decide what to do after fallback attempt."""
            if state.get("error") is None:
                return "done"
            else:
                return "error"

        # Build the graph
        graph = StateGraph(AgentState)

        graph.add_node("process", process_message)
        graph.add_node("fallback", try_fallback)
        graph.add_node("error", handle_error)

        graph.add_edge(START, "process")
        graph.add_conditional_edges(
            "process",
            route_after_process,
            {"done": END, "fallback": "fallback", "error": "error"},
        )
        graph.add_conditional_edges(
            "fallback",
            route_after_fallback,
            {"done": END, "error": "error"},
        )
        graph.add_edge("error", END)

        return graph.compile()

    @traceable(name="production_agent_invoke")
    def invoke(self, message: str) -> dict:
        """
        Invoke the agent with a user message.
        Returns: {"response": str, "model_used": str, "error": str | None}
        """
        result = self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "error": None,
            "retry_count": 0,
            "model_used": "",
        })

        return {
            "response": result["messages"][-1].content,
            "model_used": result.get("model_used", "unknown"),
            "error": result.get("error"),
        }

production_agent = ProductionAgent()
# Compatibility layer
compiled_agent = production_agent
