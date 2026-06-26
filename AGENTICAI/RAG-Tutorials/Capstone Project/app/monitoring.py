import logging
import json
import time
import threading
from datetime import datetime, timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    """Format log records as JSON for log aggregation (ELK, Datadog, etc.)."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        # Merge any extra data attached to the record
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
        return json.dumps(log_obj)

def get_logger(name: str = "production-api") -> logging.Logger:
    """Create a structured JSON logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

class MetricsCollector:
    """
    Collects and aggregates application metrics.
    In production, replace with Prometheus client:
        from prometheus_client import Counter, Histogram
    """
    def __init__(self):
        self._requests_total = 0
        self._errors_total = 0
        self._latency_sum = 0.0
        self._latency_count = 0
        self._tokens_input = 0
        self._tokens_output = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._lock = threading.Lock()

    def record_request(
        self,
        latency_ms: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        error: bool = False,
        cache_hit: bool = False,
    ) -> None:
        with self._lock:
            self._requests_total += 1
            self._latency_sum += latency_ms
            self._latency_count += 1
            self._tokens_input += input_tokens
            self._tokens_output += output_tokens
            
            if error:
                self._errors_total += 1
            if cache_hit:
                self._cache_hits += 1
            else:
                self._cache_misses += 1

    def get_metrics(self) -> dict:
        with self._lock:
            total = self._requests_total
            error_rate = self._errors_total / total if total > 0 else 0.0
            avg_latency = self._latency_sum / self._latency_count if self._latency_count > 0 else 0.0
            cache_total = self._cache_hits + self._cache_misses
            hit_rate = self._cache_hits / cache_total if cache_total > 0 else 0.0
            
            return {
                "total_requests": self._requests_total,
                "total_errors": self._errors_total,
                "error_rate": error_rate,
                "average_latency_ms": avg_latency,
                "cache_hit_rate": hit_rate,
                "total_input_tokens": self._tokens_input,
                "total_output_tokens": self._tokens_output,
            }

class RequestTimer:
    """Context manager to measure request execution time."""
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.latency_ms = (time.perf_counter() - self.start_time) * 1000.0
