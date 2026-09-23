---
title: "Distributed Caching"
description: Scale reads with Redis/Memcached, consistent hashing and cache invalidation
---

# Distributed Caching <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../web/proficient/databases/">Database Programming</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why and where to cache
- [x] The cache-aside pattern
- [x] Distribute keys with consistent hashing
- [x] Handle invalidation and cache stampedes
- [x] Use Redis and Memcached from Python

---

## Why cache

A cache stores expensive-to-compute or slow-to-fetch data in fast memory so repeated requests skip the work. In a distributed system, a shared cache (Redis, Memcached) sits between your app servers and the database, absorbing read load that would otherwise hammer the DB.

```
   app  ──▶  cache (fast, in-memory)  ──miss──▶  database (slow, authoritative)
        ◀──  hit (returns instantly)  ◀────────
```

The two hard problems (as the saying goes) are **cache invalidation** and **naming things**. We'll focus on the first — plus how to spread data across many cache servers.

---

## The cache-aside pattern

The most common strategy: the application checks the cache first, and on a miss, loads from the database and populates the cache.

```python
def get_user(user_id: int, cache, db) -> dict:
    key = f"user:{user_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached                       # cache hit — fast path

    user = db.load_user(user_id)            # cache miss — go to source
    cache.set(key, user, ttl=300)           # populate for next time (5 min)
    return user
```

**On write**, you must keep the cache consistent — usually by *invalidating* (deleting) the key so the next read reloads fresh data:

```python
def update_user(user_id: int, data: dict, cache, db) -> None:
    db.update_user(user_id, data)
    cache.delete(f"user:{user_id}")         # invalidate — don't leave stale data
```

!!! tip "Delete, don't update, the cache on writes"
    Deleting the key (letting the next read repopulate) is simpler and safer than trying to update the cached value in place. Updating in place risks races where a stale write lands after a fresh one. "Invalidate and reload" sidesteps that.

---

## Distributing keys with consistent hashing

With many cache servers, which server holds `user:42`? The naive answer — `hash(key) % num_servers` — has a fatal flaw: **add or remove one server and *almost every* key remaps**, causing a cache-wide miss storm that stampedes the database.

**Consistent hashing** solves this: hash both keys *and* servers onto a ring, and each key goes to the next server clockwise. Adding a server only remaps the keys near it. Fully runnable:

```python
import hashlib

class HashRing:
    def __init__(self, nodes: list[str], vnodes: int = 100) -> None:
        self.vnodes = vnodes
        self.ring: dict[int, str] = {}
        for n in nodes:
            self._add(n)
        self.sorted_keys = sorted(self.ring)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _add(self, node: str) -> None:
        for i in range(self.vnodes):                 # virtual nodes for even spread
            self.ring[self._hash(f"{node}:{i}")] = node

    def get_node(self, key: str) -> str:
        h = self._hash(key)
        for k in self.sorted_keys:
            if h <= k:
                return self.ring[k]
        return self.ring[self.sorted_keys[0]]        # wrap around the ring
```

Measuring how many keys move when we grow from 3 to 4 servers:

```python
ring = HashRing(["cache1", "cache2", "cache3"])
keys = [f"user:{i}" for i in range(1000)]
before = {k: ring.get_node(k) for k in keys}

ring2 = HashRing(["cache1", "cache2", "cache3", "cache4"])
after = {k: ring2.get_node(k) for k in keys}

moved = sum(1 for k in keys if before[k] != after[k])
print(f"keys moved when adding 4th node: {moved}/1000 ({moved/10:.1f}%)")
```

Output:

```text
keys moved when adding 4th node: 272/1000 (27.2%)
```

Only ~27% of keys moved when adding a server — close to the theoretical ideal of `1/4`. With naive modulo hashing, adding a 4th server would remap roughly **75%** of keys, triggering a database-crushing miss storm. The **virtual nodes** (100 ring positions per server) keep the load evenly balanced; without them, keys would clump unevenly.

---

## Cache stampedes

When a popular key expires, many requests miss simultaneously and all hit the database at once — a **stampede** (or "thundering herd") that can overwhelm it. Common defenses:

- **Locking / single-flight** — the first request to miss acquires a lock and recomputes; others wait for its result instead of all recomputing.
- **Early/probabilistic refresh** — refresh a key slightly *before* it expires, so it never fully lapses under load.
- **Stale-while-revalidate** — serve the stale value while one background task refreshes it.

```python
# single-flight sketch: only one caller recomputes a missing key
def get_with_lock(key, cache, db, lock):
    value = cache.get(key)
    if value is not None:
        return value
    with lock:                              # only one thread enters
        value = cache.get(key)              # double-check — someone may have filled it
        if value is None:
            value = db.load(key)
            cache.set(key, value, ttl=300)
        return value
```

---

## Redis and Memcached from Python

```python
import redis   # pip install redis

r = redis.Redis(host="localhost", port=6379)
r.set("user:42", "alice", ex=300)     # ex = TTL in seconds
print(r.get("user:42"))               # -> b'alice'
```

!!! note "Redis snippet needs a running Redis server"
    The `redis` client code follows the documented API and isn't run-verified here (the cache-aside logic and consistent-hashing ring above **are** tested). **Redis** offers rich types (lists, sets, sorted sets), persistence, and pub/sub; **Memcached** is simpler and pure-cache. Redis is the common default unless you specifically want Memcached's simplicity.

**Redis vs Memcached, briefly:** Redis = more features (data structures, persistence, replication, built-in clustering). Memcached = dead-simple, multi-threaded, pure key/value. Pick Redis unless you have a specific reason not to.

---

## Practice exercises

1. Add a `remove_node` method to `HashRing` and measure how many keys move when a server is removed (should again be a minority).
2. Show the naive-modulo problem: implement `hash(key) % n` placement and measure how many keys move going from 3 to 4 servers (expect ~75%).
3. Implement cache-aside with a simple dict as the cache and a fake db, and add TTL expiry.
4. Extend the single-flight sketch and write a test proving the db is loaded only once for concurrent misses of the same key.
5. Explain why deleting a key on write is safer than updating the cached value in place.
