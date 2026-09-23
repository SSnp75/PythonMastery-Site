---
title: "Distributed Queues"
description: Message queues and streams with RabbitMQ and Kafka — delivery guarantees and ordering
---

# Distributed Queues <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../web/expert/event-driven-architecture/">Event-driven Architecture</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why services communicate through queues
- [x] RabbitMQ (queue) vs Kafka (log) models
- [x] The three delivery guarantees
- [x] Build an idempotent consumer (handle duplicates)
- [x] Message ordering and consumer groups

---

## Why queues

When services talk directly (service A calls service B over HTTP), A is blocked while B works, and if B is down, A fails. A **message queue** sits between them: A publishes a message and moves on; B consumes it when ready. This **decouples** producers from consumers in time — B can be slow, restart, or scale out, and A never notices.

```
   producer ──▶ [ queue / log ]  ──▶ consumer(s)
              (buffers, persists,      (process when ready,
               absorbs bursts)          scale independently)
```

Queues give you buffering (absorb traffic spikes), resilience (messages survive a consumer crash), and independent scaling. They're the backbone of [event-driven](../web/expert/event-driven-architecture.md) systems.

---

## RabbitMQ vs Kafka: two models

The two dominant systems embody different models:

| | **RabbitMQ** (queue) | **Kafka** (log) |
|---|---|---|
| Model | Messages *pushed* to consumers, removed when acked | Append-only *log*; consumers *pull* and track their position |
| After consumption | Message gone | Message retained (replayable) |
| Ordering | Per-queue | Per-partition |
| Strength | Flexible routing, work queues | High throughput, replay, streaming |
| Reads | Once (then deleted) | Many consumers, each at its own offset |

**RabbitMQ** is a traditional broker — great for task distribution and complex routing. **Kafka** is a distributed commit log — great for high-volume event streams you may want to replay or feed to multiple independent consumers.

Producer/consumer sketch with RabbitMQ (`pika`):

```python
import pika, json   # pip install pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
ch = conn.channel()
ch.queue_declare(queue="tasks", durable=True)        # survive broker restart
ch.basic_publish(exchange="", routing_key="tasks",
                 body=json.dumps({"id": "m1", "job": "resize"}),
                 properties=pika.BasicProperties(delivery_mode=2))  # persistent
```

!!! note "Broker snippets need a running RabbitMQ/Kafka"
    The `pika` code follows the documented API and isn't run-verified here. The **idempotent consumer logic below is pure Python and tested** — and it's the part that most affects correctness.

---

## Delivery guarantees

No broker can give you everything; you choose a point on this spectrum:

- **At-most-once** — fire and forget. Fast, but messages can be lost (consumer crashes before processing). OK for disposable data (metrics samples).
- **At-least-once** — the broker redelivers until acknowledged. **No loss, but duplicates happen.** The common default.
- **Exactly-once** — no loss, no duplicates. The ideal, but genuinely hard and expensive; often *approximated* with at-least-once delivery + idempotent consumers.

The practical reality: **most systems use at-least-once and make consumers idempotent.** That combination gives you no-loss delivery while neutralizing the duplicates.

---

## The idempotent consumer

Since at-least-once means the same message can arrive twice (redelivery after a timeout, a retry, a broker hiccup), your consumer must produce the **same effect whether it processes a message once or many times**. The standard technique: track processed message IDs and skip duplicates. Fully runnable:

```python
class IdempotentConsumer:
    def __init__(self) -> None:
        self.processed: set[str] = set()
        self.effects: list[str] = []

    def handle(self, msg_id: str, payload: str) -> bool:
        if msg_id in self.processed:
            return False                     # duplicate — skip, no double effect
        self.processed.add(msg_id)
        self.effects.append(payload)         # the real side effect — happens once
        return True
```

```python
c = IdempotentConsumer()
print(c.handle("m1", "charge $10"))    # True  — processed
print(c.handle("m1", "charge $10"))    # False — same id redelivered, ignored
print(c.handle("m2", "charge $20"))    # True  — new message
print("effects:", c.effects)
```

Output:

```text
True
False
charge $20    ← (from the print of the third handle returning True)
effects: ['charge $10', 'charge $20']
```

The redelivered `m1` is skipped, so `charge $10` happens exactly once even though the message arrived twice. This is how you turn at-least-once delivery into effectively-once *processing* — the pragmatic path to "exactly once" behavior.

!!! tip "Idempotency is the real 'exactly once'"
    True exactly-once delivery across a network is extremely hard. The battle-tested approach is at-least-once delivery + an idempotent consumer (dedup by message id, or design operations that are naturally idempotent like "set balance to X" rather than "add X"). In production, store processed IDs in a database, not a set, so dedup survives restarts.

---

## Ordering and consumer groups

- **Ordering** is only guaranteed within a single queue (RabbitMQ) or partition (Kafka) — *not* globally across partitions. If you need related messages ordered, route them to the same partition (e.g. partition by `user_id` so one user's events stay ordered).
- **Consumer groups** (Kafka) let many consumers share the load: each partition is read by exactly one consumer in the group, so you scale out by adding partitions and consumers. This is how you process a high-volume stream in parallel while preserving per-partition order.

**Dead-letter queues** catch messages that repeatedly fail processing, so one poison message doesn't block the queue or retry forever — it's set aside for inspection.

---

## Practice exercises

1. Make `IdempotentConsumer` persist `processed` ids to a file (or sqlite) so dedup survives a restart.
2. Add a max-processed-set eviction (e.g. keep only the last N ids) and discuss the risk it introduces.
3. Model a dead-letter path: after 3 failed attempts, route a message to a `dead_letter` list instead of retrying forever.
4. Explain why partitioning by `user_id` preserves per-user ordering but not global ordering.
5. Give an example operation that is *naturally* idempotent (needs no dedup) and one that isn't.
