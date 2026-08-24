---
title: Metrics & Monitoring
description: Prometheus, StatsD, Grafana dashboards and application metrics
---

# Metrics & Monitoring <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>📡 Observability Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## Prometheus metrics with Python

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
import time, random

# ─── Define metrics ───────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
)

ITEMS_IN_QUEUE = Gauge(
    "queue_size",
    "Number of items in processing queue",
)

# ─── Instrument code ─────────────────────────────
def handle_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status="200").inc()

    with REQUEST_DURATION.labels(endpoint=endpoint).time():
        # Actual request handling
        time.sleep(random.uniform(0.01, 0.5))

    ACTIVE_CONNECTIONS.inc()
    # ... do work ...
    ACTIVE_CONNECTIONS.dec()

# ─── Expose metrics endpoint ──────────────────────
start_http_server(9090)   # Prometheus scrapes http://localhost:9090/metrics

# Simulate traffic
while True:
    handle_request("GET", "/api/users")
    handle_request("POST", "/api/orders")
    time.sleep(0.1)
```

### Metric types:

| Type | Purpose | Example |
|---|---|---|
| **Counter** | Monotonically increasing | Total requests, errors, bytes sent |
| **Histogram** | Distribution of values | Request duration, response size |
| **Gauge** | Can go up or down | Active connections, queue size, temperature |
| **Summary** | Like histogram, but calculates percentiles client-side | Less common |

---

## FastAPI integration

```python
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import time

app = FastAPI()

REQUEST_COUNT = Counter("requests_total", "Total requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency", ["path"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(path=request.url.path).observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## Custom business metrics

```python
# Track what matters to your business
ORDERS_PLACED = Counter("orders_placed_total", "Orders placed", ["region", "payment_method"])
ORDER_VALUE = Histogram("order_value_dollars", "Order value", buckets=[10, 25, 50, 100, 250, 500, 1000])
CONVERSION_RATE = Gauge("conversion_rate", "Current conversion rate")

def place_order(order):
    ORDERS_PLACED.labels(region=order.region, payment_method=order.payment).inc()
    ORDER_VALUE.observe(order.total)
```

---

## Grafana dashboard queries (PromQL)

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m]))

# Active connections
active_connections
```

---

## Alerting rules

```yaml
# prometheus/alerts.yml
groups:
  - name: app-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency above 2 seconds"
```

---

## Practice Exercises

1. **Instrument a FastAPI app** with request count, latency histogram and active connections.
2. **Create a Grafana dashboard** showing request rate, error rate, p95 latency and queue size.
3. **Set up alerting** — alert when error rate exceeds 1% or latency exceeds 500ms.
4. **Add business metrics** — track order value, conversion rate and user signups.
5. **Build a health check endpoint** that reports system status (CPU, memory, DB connectivity).
