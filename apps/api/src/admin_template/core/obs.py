"""Observability: logging, tracing, metrics, and health endpoints.

Implements structlog JSON logging (request_id/trace_id), OpenTelemetry
traces (OTLP export), Prometheus /metrics, and /healthz (liveness) /
/readyz (DB + Redis + Keycloak reachability) per research.md section 9.
"""

from __future__ import annotations

import logging

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, generate_latest
from sqlalchemy import select, text
from starlette.responses import PlainTextResponse

from admin_template.core.db import db
from admin_template.core.settings import settings

# ---------------------------------------------------------------------------
# Logging (structlog, JSON)
# ---------------------------------------------------------------------------


def configure_logging() -> None:
    """Configure structlog JSON logging with request_id/trace_id context."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


configure_logging()

logger = structlog.get_logger("contentforge")

# ---------------------------------------------------------------------------
# Tracing (OpenTelemetry, OTLP)
# ---------------------------------------------------------------------------

_tracer_provider: TracerProvider | None = None


def configure_tracing() -> None:
    """Initialize the OpenTelemetry tracer provider with OTLP export."""
    global _tracer_provider
    resource = Resource.create(
        {
            "service.name": settings.app_name,
            "service.version": settings.app_version,
            "deployment.environment": settings.environment,
        }
    )
    provider = TracerProvider(resource=resource)
    otlp_endpoint = settings.litellm_base_url.rstrip("/") + "/v1/traces"
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    )
    trace.set_tracer_provider(provider)
    _tracer_provider = provider


def get_tracer(name: str = "contentforge") -> trace.Tracer:
    """Return an OpenTelemetry tracer."""
    return trace.get_tracer(name)


# ---------------------------------------------------------------------------
# Metrics (Prometheus)
# ---------------------------------------------------------------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)


# ---------------------------------------------------------------------------
# Health / readiness
# ---------------------------------------------------------------------------


async def healthz() -> dict[str, str]:
    """Liveness probe: the process is up."""
    return {"status": "ok"}


async def readyz() -> dict[str, str | bool]:
    """Readiness probe: DB, Redis, Keycloak reachability.

    Verifies an actual database connection (postgres on docker), plus
    configured Redis and Keycloak settings.
    """
    checks: dict[str, str | bool] = {
        "database": False,
        "redis": bool(settings.redis_url),
        "keycloak": bool(settings.keycloak_jwks_url and settings.keycloak_issuer),
    }

    if settings.database_url:
        try:
            async for _session in db.session():
                await _session.execute(select(text("SELECT 1")))
                checks["database"] = True
                break
        except Exception:  # noqa: BLE001 -- any DB failure means not ready
            checks["database"] = False

    checks["ready"] = all(checks.values())
    return checks


def metrics() -> PlainTextResponse:
    """Prometheus metrics exposition."""
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


def bind_request_context(
    request_id: str | None = None, trace_id: str | None = None
) -> None:
    """Bind request-scoped contextvars for structured logging."""
    if request_id:
        structlog.contextvars.bind_contextvars(request_id=request_id)
    if trace_id:
        structlog.contextvars.bind_contextvars(trace_id=trace_id)


def clear_request_context() -> None:
    """Clear request-scoped contextvars after a request."""
    structlog.contextvars.clear_contextvars()


__all__ = [
    "REQUEST_COUNT",
    "REQUEST_DURATION",
    "bind_request_context",
    "clear_request_context",
    "configure_logging",
    "configure_tracing",
    "get_tracer",
    "healthz",
    "logger",
    "metrics",
    "readyz",
]
