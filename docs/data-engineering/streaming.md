---
title: Streaming (Kafka)
description: Real-time data pipelines with Kafka, producers, consumers and stream processing
---

# Streaming (Kafka) <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🔄 Data Engineering · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Kafka producer

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Send events
for i in range(100):
    event = {"user_id": i, "action": "page_view", "timestamp": "2026-08-23T12:00:00"}
    producer.send("user-events", value=event)
    print(f"  Sent event {i}")

producer.flush()   # ensure all messages are sent
producer.close()
```

---

## Kafka consumer

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "user-events",
    bootstrap_servers=["localhost:9092"],
    group_id="my-consumer-group",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

print("Listening for events...")
for message in consumer:
    event = message.value
    print(f"  Received: {event['action']} from user {event['user_id']}")
    # Process event (store, transform, trigger actions)
```

---

## Stream processing pattern

```python
import asyncio
from kafka import KafkaConsumer, KafkaProducer
import json

def process_stream():
    """Read from one topic, process, write to another."""
    consumer = KafkaConsumer("raw-events", bootstrap_servers=["localhost:9092"],
                             value_deserializer=lambda m: json.loads(m.decode()))
    producer = KafkaProducer(bootstrap_servers=["localhost:9092"],
                              value_serializer=lambda v: json.dumps(v).encode())

    for message in consumer:
        event = message.value
        # Transform
        enriched = {
            **event,
            "processed_at": datetime.utcnow().isoformat(),
            "is_premium": event.get("total_spend", 0) > 1000,
        }
        # Write to enriched topic
        producer.send("enriched-events", value=enriched)
```

---

## Practice Exercises

1. **Build a producer** that generates fake events at 100/second.
2. **Build a consumer** that aggregates events into 1-minute windows.
3. **Implement exactly-once** semantics using transactions.
4. **Build a dead-letter queue** — failed messages go to a separate topic.
5. **Monitor lag** — track how far behind the consumer is.
