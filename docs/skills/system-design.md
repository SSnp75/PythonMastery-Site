---
title: System Design
description: Designing scalable systems — architecture patterns, trade-offs and interview preparation
---

# System Design <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🧠 Soft Skills · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
  </div>
</div>

---

## The system design framework

```
1. REQUIREMENTS   — What exactly are we building? (functional + non-functional)
2. ESTIMATION     — How much data? How many users? QPS?
3. HIGH-LEVEL     — Major components and how they connect
4. DETAILED       — Dive into the hardest parts
5. TRADE-OFFS     — Why this design over alternatives?
```

---

## Example: Design a URL shortener

### Requirements
- Shorten a URL → return short code (7 chars)
- Redirect short code → original URL
- 100M URLs, 1000 reads/sec, 10 writes/sec
- Analytics (click count)

### High-level design

```
Client → Load Balancer → API Server → Database
                              ↓
                         Cache (Redis)
```

### Data model

```python
# URL mapping
class URL:
    short_code: str    # "abc1234" (primary key)
    original_url: str  # "https://very-long-url.com/..."
    created_at: datetime
    click_count: int
    user_id: int | None
```

### Core algorithm

```python
import hashlib
import string

ALPHABET = string.ascii_letters + string.digits   # 62 chars
BASE = len(ALPHABET)

def encode_id(num: int) -> str:
    """Convert numeric ID to base-62 string."""
    if num == 0:
        return ALPHABET[0]
    result = []
    while num:
        result.append(ALPHABET[num % BASE])
        num //= BASE
    return "".join(reversed(result))

def shorten(original_url: str) -> str:
    # Option 1: Auto-increment ID → base62
    url_id = db.insert(original_url)   # returns auto-inc ID
    return encode_id(url_id)

    # Option 2: Hash-based
    hash_hex = hashlib.md5(original_url.encode()).hexdigest()
    return hash_hex[:7]   # collision possible!
```

### Scaling considerations

| Challenge | Solution |
|---|---|
| High read traffic | Redis cache (short_code → URL) |
| Database scaling | Sharding by short_code prefix |
| Analytics | Write to Kafka → batch aggregate |
| Availability | Multi-region deployment |
| Rate limiting | Redis-based sliding window |

---

## Key trade-offs to discuss

| Decision | Option A | Option B |
|---|---|---|
| SQL vs NoSQL | Consistent, ACID | Scalable, flexible schema |
| Cache invalidation | TTL-based (simple) | Event-driven (consistent) |
| Sync vs Async | Simple, consistent | Higher throughput |
| Monolith vs Micro | Simple ops | Independent scaling |
| Consistency vs Availability | Strong consistency | Eventually consistent |

---

## Common system design problems

| Problem | Key challenges |
|---|---|
| URL shortener | ID generation, caching, analytics |
| Chat system | WebSockets, presence, message ordering |
| News feed | Fan-out, ranking, personalization |
| Rate limiter | Sliding window, distributed state |
| Notification system | Multi-channel, retry, scheduling |
| File storage (Dropbox) | Chunking, sync, deduplication |
| Search engine | Inverted index, ranking, crawling |
| Payment system | Idempotency, reconciliation, fraud |

---

## Practice Exercises

1. **Design a Twitter-like feed** — handle writes from 100K users, reads from 10M users.
2. **Design a chat application** — 1:1 and group chat with read receipts and typing indicators.
3. **Design a job queue** — reliable, distributed, with retry and dead-letter queue.
4. **Design a rate limiter** — multiple algorithms (fixed window, sliding window, token bucket).
5. **Design a notification service** — email, push, SMS with batching and user preferences.
