from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import os

# Initialize tracer with safe exception catching
provider = TracerProvider()
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
except Exception as e:
    print(f"OTLP Span Exporter failed to initialize (continuing without OTLP collector): {e}")

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("supply-chain-agent")

def trace_agent_call(agent_name: str, input_data: dict):
    """Context manager to trace individual agent calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"agent.{agent_name}") as span:
                start_time = time.time()
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.input_keys", str(list(input_data.keys()) if isinstance(input_data, dict) else []))
                
                result = func(*args, **kwargs)
                
                latency_ms = (time.time() - start_time) * 1000
                span.set_attribute("agent.latency_ms", latency_ms)
                span.set_attribute("agent.success", True)
                
                return result
        return wrapper
    return decorator
