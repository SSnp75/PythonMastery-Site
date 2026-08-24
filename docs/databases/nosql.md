---
title: NoSQL (Redis, MongoDB)
description: Key-value stores, document databases, caching patterns and when to use NoSQL
---

# NoSQL <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🗄️ Databases · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Redis — in-memory key-value store

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ─── Basic key-value ──────────────────────────────
r.set("user:1:name", "Alice")
r.set("session:abc123", "user_1", ex=3600)   # expires in 1 hour
print(r.get("user:1:name"))   # Alice
print(r.ttl("session:abc123"))  # seconds remaining

# ─── Hash (object-like) ──────────────────────────
r.hset("user:1", mapping={"name": "Alice", "email": "a@b.com", "age": "30"})
print(r.hget("user:1", "name"))   # Alice
print(r.hgetall("user:1"))        # {'name': 'Alice', 'email': 'a@b.com', 'age': '30'}

# ─── List (queue/stack) ──────────────────────────
r.rpush("tasks", "task1", "task2", "task3")
task = r.lpop("tasks")   # "task1" (FIFO queue)

# ─── Set ──────────────────────────────────────────
r.sadd("online_users", "user1", "user2", "user3")
print(r.sismember("online_users", "user1"))   # True
print(r.scard("online_users"))                 # 3

# ─── Sorted set (leaderboard) ────────────────────
r.zadd("leaderboard", {"alice": 100, "bob": 85, "charlie": 92})
print(r.zrevrange("leaderboard", 0, 2, withscores=True))
# [('alice', 100.0), ('charlie', 92.0), ('bob', 85.0)]

# ─── Pub/Sub ─────────────────────────────────────
# Publisher
r.publish("notifications", '{"user": 1, "message": "hello"}')

# Subscriber
pubsub = r.pubsub()
pubsub.subscribe("notifications")
for message in pubsub.listen():
    if message["type"] == "message":
        print(f"  Got: {message['data']}")
```

### Caching pattern:

```python
import json

def get_user(user_id: int) -> dict:
    # Check cache first
    cached = r.get(f"cache:user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss — query database
    user = db.query(User).get(user_id)
    r.set(f"cache:user:{user_id}", json.dumps(user.to_dict()), ex=300)  # 5 min TTL
    return user.to_dict()
```

---

## MongoDB — document database

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["myapp"]
users = db["users"]

# ─── Insert ──────────────────────────────────────
user = {"name": "Alice", "email": "a@b.com", "age": 30, "tags": ["python", "data"]}
result = users.insert_one(user)
print(f"Inserted: {result.inserted_id}")

users.insert_many([
    {"name": "Bob", "age": 25, "city": "NYC"},
    {"name": "Charlie", "age": 35, "city": "LA"},
])

# ─── Query ────────────────────────────────────────
alice = users.find_one({"name": "Alice"})
print(alice)

# Complex queries
results = users.find({"age": {"$gt": 25}, "city": {"$in": ["NYC", "LA"]}})
for doc in results:
    print(doc["name"])

# ─── Update ───────────────────────────────────────
users.update_one({"name": "Alice"}, {"$set": {"age": 31}})
users.update_many({"city": "NYC"}, {"$inc": {"visits": 1}})

# ─── Aggregation pipeline ─────────────────────────
pipeline = [
    {"$match": {"age": {"$gte": 18}}},
    {"$group": {"_id": "$city", "avg_age": {"$avg": "$age"}, "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]
for doc in users.aggregate(pipeline):
    print(f"  {doc['_id']}: {doc['count']} users, avg age {doc['avg_age']:.1f}")
```

---

## When to use what

| Use case | Best choice |
|---|---|
| Caching, sessions, rate limiting | Redis |
| Flexible schema, documents | MongoDB |
| Relational data, transactions | PostgreSQL |
| Time-series data | TimescaleDB, InfluxDB |
| Full-text search | Elasticsearch |
| Graph relationships | Neo4j |

---

## Practice Exercises

1. **Build a session store** with Redis — create, read, expire and invalidate sessions.
2. **Implement a rate limiter** using Redis sorted sets (sliding window).
3. **Build a REST API** backed by MongoDB with full CRUD.
4. **Implement a cache-aside pattern** — cache DB results in Redis with TTL.
5. **Build a leaderboard** with Redis sorted sets — add scores, get rankings, get top N.
