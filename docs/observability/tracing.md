---
title: Distributed Tracing
description: OpenTelemetry, spans, trace context propagation and debugging distributed systems
---

# Distributed Tracing <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>📡 Observability Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## What is distributed tracing?

When a request passes through multiple services, tracing shows the full journey:

```
User → API Gateway → Order Service → Payment Service → Email Service
         2ms            150ms           500ms            100ms

Total: 752ms — tracing shows WHERE time was spent
```

---

## OpenTelemetry — the standard

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
# Export to console (dev) or OTLP collector (prod)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
# provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317")))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("my-service")

# ─── Create spans ─────────────────────────────────
def process_order(order_id: int):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        with tracer.start_as_current_span("validate_order"):
            validate(order_id)

        with tracer.start_as_current_span("charge_payment") as payment_span:
            payment_span.set_attribute("payment.method", "card")
            charge(order_id)

        with tracer.start_as_current_span("send_confirmation"):
            send_email(order_id)

        span.set_attribute("order.status", "completed")
```

---

## Auto-instrumentation (zero code changes)

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install   # installs all relevant instrumentors

# Run your app with auto-instrumentation
opentelemetry-instrument \
    --service_name my-service \
    --exporter_otlp_endpoint http://jaeger:4317 \
    python app.py
```

This automatically traces: HTTP requests (httpx, requests), database queries (SQLAlchemy, psycopg), Redis calls, etc.

---

## FastAPI integration

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# Now every request automatically gets a trace with:
# - Request method, path, status code
# - Duration
# - All downstream spans (DB queries, HTTP calls, etc.)
```

---

## Context propagation between services

```python
import httpx
from opentelemetry.propagate import inject

async def call_downstream_service(order_id: int):
    """Propagate trace context to another service."""
    headers = {}
    inject(headers)   # injects traceparent header

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://payment-service:8001/charge",
            json={"order_id": order_id},
            headers=headers,   # trace context propagated!
        )
        return response.json()
```

The downstream service extracts the trace context and continues the same trace.

---

## Practice Exercises

1. **Instrument a FastAPI app** with OpenTelemetry — trace requests end-to-end.
2. **Add custom spans** for database queries and external API calls.
3. **Set up Jaeger** locally and visualize traces in the UI.
4. **Propagate context** between two services and verify the trace connects.
5. **Add span events and attributes** for debugging (user_id, error details).
