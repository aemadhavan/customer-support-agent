"""
Telemetry and OpenTelemetry Instrumentation for Customer Support Agent.
Satisfies SPEC §10, O-1, O-2, O-3, O-4, and TECHNICAL Stage 5.
"""

import os
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes

_INITIALIZED = False
_TRACER: Optional[trace.Tracer] = None

def init_telemetry(
    endpoint: str = "http://localhost:6006/v1/traces",
    project_name: str = "customer-support"
) -> trace.Tracer:
    """
    Initializes global OpenTelemetry TracerProvider with OTLP export to Phoenix.
    Instruments Google GenAI SDK calls and configures the OpenInference project name.
    """
    global _INITIALIZED, _TRACER
    if _INITIALIZED and _TRACER is not None:
        return _TRACER

    # Configure Resource with service name and Phoenix project name
    resource = Resource.create({
        "service.name": "customer-support",
        "openinference.project.name": project_name
    })

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint)
    # SimpleSpanProcessor ensures spans are immediately flushed on completion
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    
    trace.set_tracer_provider(provider)
    GoogleGenAIInstrumentor().instrument(tracer_provider=provider)

    _TRACER = trace.get_tracer("customer_support")
    _INITIALIZED = True
    return _TRACER

def get_tracer() -> trace.Tracer:
    """Returns the initialized tracer, initializing with defaults if necessary."""
    global _TRACER
    if _TRACER is None:
        return init_telemetry()
    return _TRACER

def format_trace_url(trace_id_hex: str, project_name: str = "customer-support") -> str:
    """Formats the direct URL to inspect the trace in Phoenix UI (SPEC O-4)."""
    return f"http://localhost:6006/projects/{project_name}/traces/{trace_id_hex}"
