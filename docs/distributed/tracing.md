---
title: "Distributed Tracing"
description: Follow a request across services with traces, spans and OpenTelemetry
---

# Distributed Tracing <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../web/expert/microservices/">Microservices</a>, <a href="../embedded/system-monitoring/">System Monitoring</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why tracing exists (debugging across services)
- [x] Traces, spans and context propagation
- [x] Build a span tree and reconstruct it
- [x] Instrument Python with OpenTelemetry
- [x] Read a trace to find a bottleneck

---

## The problem: where did the time go?

In a monolith, a slow request shows up in one stack trace. In [microservices](../web/expert/microservices.md), a single user request might touch a dozen services — API gateway → auth → orders → inventory → payment → database. When it's slow, *which* service is to blame? Logs on each service can't easily be stitched together. **Distributed tracing** solves this by following one request across every service it touches and timing each step.

```
   request T1
   ├─ http_request           [██████████████████] 210ms
   │  ├─ auth_check          [██]                  15ms
   │  ├─ db_query            [████████]            80ms
   │  │  └─ row_parse        [█]                    5ms
   │  └─ payment_call        [████████████]        90ms   ← the bottleneck
```

---

## Traces, spans, and context

- **Trace** — the whole journey of one request, identified by a **trace ID** shared by every step.
- **Span** — one unit of work within the trace (a function, an HTTP call, a DB query), with a start, a duration, and a **span ID**.
- **Parent/child** — spans nest: a span records its parent's ID, forming a tree that mirrors the call structure.
- **Context propagation** — the trace ID and current span ID are passed *across service boundaries* (usually in HTTP headers, like `traceparent`), so a downstream service attaches its spans to the same trace.

Context propagation is the crux: without passing the trace ID along, each service would start its own disconnected trace and you'd lose the end-to-end picture.

---

## Modeling a span tree

The core data model is simple — spans sharing a trace ID, linked by parent IDs. Fully runnable:

```python
from dataclasses import dataclass

@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None = None
    duration_ms: float = 0.0

class Tracer:
    def __init__(self) -> None:
        self._n = 0
        self.spans: list[Span] = []

    def start(self, name: str, trace_id: str, parent: Span | None = None) -> Span:
        self._n += 1
        span = Span(name, trace_id, span_id=f"s{self._n}",
                    parent_id=parent.span_id if parent else None)
        self.spans.append(span)
        return span
```

Building a trace for one request and reconstructing the tree:

```python
t = Tracer()
root  = t.start("http_request", trace_id="T1")
db    = t.start("db_query",   trace_id="T1", parent=root)
cache = t.start("cache_get",  trace_id="T1", parent=root)
parse = t.start("row_parse",  trace_id="T1", parent=db)

root_children = [s.name for s in t.spans if s.parent_id == root.span_id]
db_children   = [s.name for s in t.spans if s.parent_id == db.span_id]
print("root children:", root_children)
print("db children:  ", db_children)
```

Output:

```text
root children: ['db_query', 'cache_get']
db children:   ['row_parse']
```

All four spans share `trace_id="T1"`, and the parent links let us rebuild the exact call tree: `http_request` has two children (`db_query`, `cache_get`), and `db_query` has one (`row_parse`). A tracing UI (Jaeger, Zipkin) takes exactly this data — spans with shared trace IDs and parent links, plus durations — and draws the waterfall chart above, so the slowest span jumps out.

---

## OpenTelemetry: the standard

You don't hand-roll tracing in production — you use **OpenTelemetry (OTel)**, the vendor-neutral standard for instrumentation. It generates spans, propagates context across services, and exports to any backend (Jaeger, Zipkin, Datadog, Grafana Tempo).

```python
from opentelemetry import trace   # pip install opentelemetry-api opentelemetry-sdk

tracer = trace.get_tracer(__name__)

def handle_request():
    with tracer.start_as_current_span("http_request"):
        result = query_db()          # child spans nest automatically
        return result

def query_db():
    with tracer.start_as_current_span("db_query"):
        ...
```

!!! note "OTel snippet needs the packages + a backend"
    This follows OpenTelemetry's documented API and isn't run-verified here (the span-tree model above **is** tested). OTel's big win: the `with tracer.start_as_current_span(...)` context manager handles parent/child linking and context propagation for you — including across HTTP calls when you enable its auto-instrumentation for frameworks like FastAPI and `requests`.

---

## Reading a trace to debug

The workflow once tracing is in place:

1. A request is slow → find its trace by ID (often logged with the request).
2. Look at the **waterfall**: which span has the longest duration?
3. Drill in — is the slow span doing real work, or *waiting* on a downstream call?
4. Follow the tree to the leaf that's actually slow (the payment call, a specific query).

This turns "the checkout is slow sometimes" into "the payment service's fraud-check span takes 2s on 5% of requests" — a specific, fixable finding. Tracing complements [metrics](../embedded/system-monitoring.md) (which tell you *that* something's slow) by telling you *where*.

---

## The three pillars of observability

Tracing is one of three complementary signals:

- **Metrics** — aggregate numbers over time (request rate, error %, p99 latency). *Is* something wrong?
- **Logs** — discrete event records. *What* happened at this point?
- **Traces** — request flow across services. *Where* did the time/error occur?

Modern observability uses all three, often correlated (a trace ID in your logs links a log line to its trace).

---

## Practice exercises

1. Add `duration_ms` to each span in the `Tracer` example and write a function that finds the single slowest span in a trace.
2. Write a function that pretty-prints the span tree with indentation reflecting depth (walk parent links).
3. Model context propagation: write a `to_headers(span)` and `from_headers(headers)` pair that would carry trace/span IDs across an HTTP call.
4. Given a trace where a parent span is 200ms but its children sum to 40ms, explain what the missing 160ms likely represents.
5. Explain how a trace ID in your log lines helps you jump between logs and traces during an incident.
