---
title: Microservices Architecture
description: Service boundaries, communication patterns, orchestration and observability
---

# Microservices Architecture <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="../proficient/frameworks/">Web Frameworks</a>, <a href="../../systems/proficient/asyncio/">Asyncio</a></span>
  </div>
</div>

---

## When to use microservices

!!! warning "Start monolith, extract later"
    Don't start with microservices. Start with a well-structured monolith and extract services when you have:
    
    - Clear domain boundaries
    - Different scaling needs per component
    - Multiple teams that need to deploy independently
    - Performance bottlenecks in specific areas

### Monolith vs Microservices

| Aspect | Monolith | Microservices |
|---|---|---|
| Deployment | Single unit | Independent services |
| Scaling | Scale everything | Scale per service |
| Complexity | Lower operational | Higher operational |
| Data | Shared database | Database per service |
| Communication | Function calls | Network (HTTP, gRPC, events) |
| Testing | Easy integration tests | Complex end-to-end tests |
| Team size | < 10 developers | Multiple teams (> 20) |

---

## Service decomposition

### Bounded contexts (from DDD)

Each service owns a **bounded context** — a clear domain boundary:

```
E-commerce Platform:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Catalog   │  │   Orders    │  │   Payment   │
│  Service    │  │  Service    │  │  Service    │
│             │  │             │  │             │
│ - Products  │  │ - Orders    │  │ - Charges   │
│ - Categories│  │ - LineItems │  │ - Refunds   │
│ - Search    │  │ - Shipping  │  │ - Invoices  │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ CatalogDB│    │ OrdersDB │    │ PaymentDB│
  └─────────┘    └─────────┘    └─────────┘
```

---

## Communication patterns

### Synchronous — REST / gRPC

```python
# Service A calls Service B via HTTP
import httpx

class OrderService:
    def __init__(self):
        self.catalog_url = "http://catalog-service:8001"

    async def create_order(self, product_id: int, quantity: int):
        async with httpx.AsyncClient() as client:
            # Check product availability
            response = await client.get(
                f"{self.catalog_url}/products/{product_id}"
            )
            product = response.json()

            if product["stock"] < quantity:
                raise ValueError("Insufficient stock")

            # Create order
            order = await self._save_order(product_id, quantity, product["price"])

            # Reserve stock
            await client.post(
                f"{self.catalog_url}/products/{product_id}/reserve",
                json={"quantity": quantity},
            )
            return order
```

### Asynchronous — Event-driven

```python
# Using Redis Pub/Sub or a message broker
import redis.asyncio as redis
import json

class EventBus:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost")

    async def publish(self, event_type: str, data: dict):
        message = json.dumps({"type": event_type, "data": data})
        await self.redis.publish("events", message)

    async def subscribe(self, handler):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("events")
        async for message in pubsub.listen():
            if message["type"] == "message":
                event = json.loads(message["data"])
                await handler(event)

# Order Service publishes
bus = EventBus()
await bus.publish("order.created", {
    "order_id": 123,
    "product_id": 456,
    "quantity": 2,
})

# Inventory Service listens
async def handle_event(event):
    if event["type"] == "order.created":
        await reduce_stock(event["data"]["product_id"], event["data"]["quantity"])

await bus.subscribe(handle_event)
```

---

## Patterns

### API Gateway

```python
# Single entry point that routes to services
from fastapi import FastAPI, Request
import httpx

gateway = FastAPI()

SERVICES = {
    "catalog": "http://catalog:8001",
    "orders": "http://orders:8002",
    "users": "http://users:8003",
}

@gateway.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return {"error": "Unknown service"}, 404

    url = f"{SERVICES[service]}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            content=await request.body(),
            headers=dict(request.headers),
        )
        return response.json()
```

### Circuit Breaker

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing — reject all calls
    HALF_OPEN = "half_open" # testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

async def call_payment_service(order_id):
    return await breaker.call(httpx.AsyncClient().post, f"{PAYMENT_URL}/charge", json={"order_id": order_id})
```

### Saga Pattern (distributed transactions)

```python
class OrderSaga:
    """Coordinate a multi-step business process across services."""

    def __init__(self):
        self.steps_completed = []

    async def execute(self, order_data: dict):
        try:
            # Step 1: Reserve inventory
            await self._reserve_inventory(order_data)
            self.steps_completed.append("inventory")

            # Step 2: Process payment
            await self._process_payment(order_data)
            self.steps_completed.append("payment")

            # Step 3: Create shipment
            await self._create_shipment(order_data)
            self.steps_completed.append("shipment")

        except Exception as e:
            # Compensating transactions (rollback in reverse order)
            await self._compensate()
            raise

    async def _compensate(self):
        for step in reversed(self.steps_completed):
            if step == "shipment":
                await self._cancel_shipment()
            elif step == "payment":
                await self._refund_payment()
            elif step == "inventory":
                await self._release_inventory()
```

---

## Observability

### Distributed tracing with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("order-service")

# Instrument
@app.post("/orders")
async def create_order(data: OrderCreate):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.product_id", data.product_id)

        with tracer.start_as_current_span("check_inventory"):
            stock = await check_inventory(data.product_id)

        with tracer.start_as_current_span("process_payment"):
            payment = await charge_card(data.amount)

        span.set_attribute("order.status", "completed")
        return {"order_id": order.id}
```

---

## Docker Compose for local development

```yaml
# docker-compose.yml
services:
  catalog:
    build: ./catalog-service
    ports: ["8001:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:pass@catalog-db/catalog

  orders:
    build: ./orders-service
    ports: ["8002:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:pass@orders-db/orders
      CATALOG_URL: http://catalog:8000

  catalog-db:
    image: postgres:16
    environment:
      POSTGRES_DB: catalog
      POSTGRES_PASSWORD: pass

  orders-db:
    image: postgres:16
    environment:
      POSTGRES_DB: orders
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7
```

---

## Practice Exercises

1. **Decompose a monolith** — take a Flask monolith app and extract 3 services with clear boundaries.
2. **Implement the Circuit Breaker pattern** with configurable threshold and recovery.
3. **Build an event-driven system** where OrderService publishes events and InventoryService + NotificationService consume them.
4. **Implement the Saga pattern** for a 3-step distributed transaction with compensating actions.
5. **Add distributed tracing** with OpenTelemetry across 2+ services.
6. **Write docker-compose.yml** for a complete local development environment.
