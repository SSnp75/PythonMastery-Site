---
title: "Event-driven Architecture"
description: Decouple components with events, handlers and message brokers
---

# Event-driven Architecture <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="microservices/">Microservices</a>, <a href="../../automation/scripting/">Automation & Scripting</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Model your system as events and reactions
- [x] Build an in-process event bus
- [x] Decouple producers from consumers
- [x] Understand brokers (RabbitMQ, Kafka) and when you need them
- [x] Weigh the tradeoffs honestly

---

## The idea

In a traditional design, a component *calls* the components it depends on: place an order, then directly call email, inventory, and analytics. Everything is wired together and knows about everything else.

Event-driven architecture inverts this. A component announces that **something happened** (an *event*) and moves on. Other components *react* if they care. The producer doesn't know or care who's listening.

```
  Direct calls (coupled):          Events (decoupled):

  place_order()                    place_order()
     ├─▶ send_email()                 └─▶ publish(OrderPlaced)
     ├─▶ update_inventory()                   │
     └─▶ record_analytics()                   ├─▶ email handler
                                              ├─▶ inventory handler
                                              └─▶ analytics handler
```

The key shift: an **event is a fact about the past** ("OrderPlaced"), not a command ("SendEmail"). The producer states the fact; consumers decide what to do about it.

---

## An in-process event bus

You don't need a message broker to get most of the decoupling benefit. Within a single process, a simple **event bus** already separates producers from consumers. Everything below is runnable.

### Define events

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Event: ...

@dataclass(frozen=True)
class OrderPlaced(Event):
    order_id: str
    amount: float

@dataclass(frozen=True)
class OrderShipped(Event):
    order_id: str
```

Events are immutable (`frozen=True`) data — they record what happened and carry the relevant facts.

### The bus

```python
from collections import defaultdict
from typing import Callable

Handler = Callable[[Event], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: dict[type, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Handler) -> None:
        self._subs[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._subs[type(event)]:
            handler(event)
```

The bus maps each event type to a list of interested handlers. `publish` looks up handlers for that exact event type and calls each one.

### Handlers

```python
def send_confirmation(e: OrderPlaced) -> None:
    print(f"Email: order {e.order_id} confirmed (${e.amount})")

def update_inventory(e: OrderPlaced) -> None:
    print(f"Inventory: reserved stock for {e.order_id}")

def notify_shipping(e: OrderShipped) -> None:
    print(f"Shipping: {e.order_id} handed to courier")
```

### Wire it up and publish

```python
bus = EventBus()
bus.subscribe(OrderPlaced, send_confirmation)
bus.subscribe(OrderPlaced, update_inventory)
bus.subscribe(OrderShipped, notify_shipping)

bus.publish(OrderPlaced(order_id="A100", amount=49.99))
bus.publish(OrderShipped(order_id="A100"))
```

Output:

```text
Email: order A100 confirmed ($49.99)
Inventory: reserved stock for A100
Shipping: A100 handed to courier
```

**What this bought us:** the code that places an order publishes `OrderPlaced` and is done. Adding a new reaction — say, a loyalty-points handler — means writing one function and one `subscribe` call. The order-placing code never changes and never even learns the new handler exists. That's the decoupling payoff.

---

## Scaling out: message brokers

The in-process bus works within one program. When components are **separate services** (or must survive restarts, or need to buffer bursts), you move the events onto a **message broker** that sits between producers and consumers over the network.

| Broker | Model | Best for |
|---|---|---|
| **RabbitMQ** | Message queue (push, routing) | Task distribution, work queues, complex routing |
| **Kafka** | Distributed log (pull, retained) | High-throughput streams, event replay, analytics |
| **Redis Pub/Sub / Streams** | Lightweight | Simple fan-out, already using Redis |

Conceptual producer/consumer with RabbitMQ (via `pika`):

```python
# producer — publishes and forgets
import pika, json

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue="orders")
channel.basic_publish(
    exchange="",
    routing_key="orders",
    body=json.dumps({"order_id": "A100", "amount": 49.99}),
)
conn.close()
```

```python
# consumer — reacts, running in a separate service
import pika, json

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue="orders")

def on_message(ch, method, properties, body):
    order = json.loads(body)
    print(f"Processing order {order['order_id']}")

channel.basic_consume(queue="orders", on_message_callback=on_message, auto_ack=True)
channel.start_consuming()   # blocks, waiting for messages
```

!!! note "This broker code needs a running RabbitMQ"
    The `pika` snippets require `pip install pika` and a RabbitMQ server, so they aren't run-verified here (unlike the in-process bus above, which is). They follow pika's documented API. The core mental model is identical to the in-process bus — publish a fact, react elsewhere — just over a network with durability.

**Delivery guarantees** you'll need to reason about with any broker:

- **At-least-once** — a message may be delivered more than once, so consumers must be *idempotent* (processing the same event twice does no harm).
- **At-most-once** — no duplicates, but messages can be lost.
- **Exactly-once** — the ideal, but genuinely hard and often approximated with idempotency + deduplication.

---

## The honest tradeoffs

Event-driven design is powerful but not free.

**Gains**
- **Loose coupling** — producers and consumers evolve independently.
- **Extensibility** — add reactions without touching producers.
- **Resilience & buffering** (with a broker) — a slow or down consumer doesn't block the producer.

**Costs**
- **Harder to follow.** There's no straight-line call stack. To answer "what happens when an order is placed?" you must find every subscriber. Good naming and a documented event catalog help.
- **Eventual consistency.** Reactions happen after the fact, so the system is briefly inconsistent. Callers can't assume the email was sent by the time `publish` returns.
- **Debugging & ordering.** Tracing a flow across handlers/services needs distributed tracing; message ordering is not guaranteed by default.
- **Error handling shifts.** A failed handler doesn't fail the producer — you need dead-letter queues, retries, and monitoring.

!!! tip "Start in-process"
    Reach for a broker only when you actually need cross-service delivery, durability, or buffering. Many systems get 80% of the benefit from a simple in-process bus and can graduate later — the event *model* stays the same.

---

## Relationship to other patterns

- **Event Sourcing** stores the events themselves as the source of truth (state is rebuilt by replaying them) — see the Distributed Systems section.
- **CQRS** often pairs with events: commands produce events; read models are updated by consuming them.
- **Microservices** frequently communicate via events to stay decoupled.

---

## Practice exercises

1. Add a `record_analytics` handler for `OrderPlaced` and confirm the order-placing code doesn't change.
2. Make the bus tolerant: wrap each handler call in try/except so one failing handler doesn't stop the others, and print which handler failed.
3. Add a wildcard subscription that receives *every* event type (useful for logging).
4. Rewrite the handlers to be `async` and make `publish` await them with `asyncio.gather`.
5. Write down which of your handlers must be idempotent if the bus were switched to at-least-once delivery, and why.
