from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="The user's message to the agent")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for continuing a conversation")

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    model_used: str
    cached: bool = False
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    checks: Dict[str, Any]

class MetricResponse(BaseModel):
    total_requests: int
    total_errors: int
    error_rate: float
    average_latency_ms: float
    cache_hit_rate: float
    total_input_tokens: int
    total_output_tokens: int

MetricsResponse = MetricResponse

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
