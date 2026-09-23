---
title: "CRDTs"
description: Conflict-free replicated data types that merge without coordination
---

# CRDTs <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="index/">Distributed Systems intro</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The problem CRDTs solve (merging without coordination)
- [x] Build a grow-only counter (G-Counter)
- [x] Build a last-write-wins register (LWW)
- [x] The three properties that make merges safe
- [x] Where CRDTs are used in the real world

---

## The problem

When data is replicated across nodes that can update independently — offline apps, multi-region databases, collaborative editors — two replicas can change the *same* value at the *same* time. When they sync, whose value wins? Locking everything to coordinate is slow and defeats the point of replication.

**CRDTs (Conflict-free Replicated Data Types)** are data structures designed so that concurrent updates **always merge to the same result, automatically, without coordination**. No locks, no consensus, no "last writer clobbers everything." Any two replicas that have seen the same set of updates converge to identical state — a property called *strong eventual consistency*.

```
   Replica A: 3 ─┐                    ┌─▶ merge → 8
                 ├─ sync (both ways) ─┤
   Replica B: 5 ─┘                    └─▶ merge → 8   (both converge)
```

---

## G-Counter: a grow-only counter

The simplest CRDT. The trick: instead of one shared number, **each node keeps its own count**, and the value is the sum. Merging takes the max per node — so no increment is ever lost. Fully runnable:

```python
class GCounter:
    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.counts: dict[str, int] = {}

    def increment(self, n: int = 1) -> None:
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + n

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> None:
        for node, cnt in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), cnt)   # max per node
```

Two nodes increment concurrently, then sync:

```python
a = GCounter("A")
b = GCounter("B")
a.increment(3)      # A's count: {A: 3}
b.increment(5)      # B's count: {B: 5}

a.merge(b)          # sync both directions
b.merge(a)

print("A value:", a.value(), " B value:", b.value())
```

Output:

```text
A value: 8  B value: 8
```

Both replicas converge to 8 — neither increment was lost. Because each node owns its own slot, there's no conflict to resolve; merge just takes the highest count seen for each node. Merging is safe to repeat: `a.merge(b)` again leaves it at 8.

!!! note "Why per-node counts?"
    A single shared integer can't merge safely: if A sees 3 and B sees 5, is the answer 5 (max) or 8 (sum)? You can't tell without knowing the history. Splitting the count per node makes the history explicit, so `max` per slot is provably correct.

---

## LWW-Register: last-write-wins

For a single value (like a user's chosen theme color), a common CRDT attaches a **timestamp** and keeps whichever write is latest:

```python
from dataclasses import dataclass

@dataclass
class LWWRegister:
    value: str = ""
    timestamp: float = 0.0

    def set(self, value: str, ts: float) -> None:
        if ts > self.timestamp:
            self.value, self.timestamp = value, ts

    def merge(self, other: "LWWRegister") -> None:
        if other.timestamp > self.timestamp:
            self.value, self.timestamp = other.value, other.timestamp
```

```python
r1 = LWWRegister()
r2 = LWWRegister()
r1.set("red", ts=10.0)
r2.set("blue", ts=12.0)      # a later write

r1.merge(r2)
r2.merge(r1)
print("r1:", r1.value, " r2:", r2.value)
```

Output:

```text
r1: blue  r2: blue
```

The later write (`blue` at t=12) wins on both replicas. Simple and convergent — but note the tradeoff: LWW **discards** the losing write. That's fine for a color preference, wrong for a bank balance.

!!! warning "LWW loses data by design"
    Last-write-wins silently drops concurrent conflicting writes. It's the right choice only when losing the older value is acceptable. It also depends on synchronized clocks — clock skew across nodes can make the "wrong" write win. For values where every update must survive, use a counter/set CRDT instead.

---

## What makes a merge safe

A CRDT merge works because it has three mathematical properties. Any operation with all three converges regardless of order or duplication:

| Property | Meaning | Why it matters |
|---|---|---|
| **Commutative** | `merge(a, b) == merge(b, a)` | Messages can arrive in any order |
| **Associative** | grouping doesn't matter | Merges can be batched arbitrarily |
| **Idempotent** | merging the same state twice = once | Duplicate/re-delivered messages are harmless |

`max` (G-Counter) and "keep latest timestamp" (LWW) both satisfy all three — which is *why* those merges are correct. This is also why CRDTs pair naturally with at-least-once message delivery ([Distributed Queues](queues.md)): duplicates don't corrupt state.

---

## The CRDT family

- **Counters** — G-Counter (increment-only), PN-Counter (increment + decrement, using two G-Counters).
- **Registers** — LWW-Register, Multi-Value Register (keeps all concurrent values for the app to resolve).
- **Sets** — G-Set (add-only), OR-Set (add/remove with unique tags).
- **Sequences** — for collaborative text editing (the basis of tools like Yjs/Automerge).

---

## Real-world use

- **Collaborative editors** (Figma, Google Docs-style tools) — merge simultaneous edits without a central lock.
- **Offline-first / local-first apps** — edit offline, sync and merge cleanly when back online.
- **Distributed databases** — Redis has built-in CRDTs (in Redis Enterprise); Riak, Azure Cosmos DB use them for multi-region writes.
- **Shopping carts** — the classic Amazon Dynamo example: merge a cart edited on your phone and laptop without losing items.

CRDTs shine exactly where [Multi-region Consistency](multi-region-consistency.md) is hard: they let every replica accept writes locally and reconcile later, no coordination required.

---

## Practice exercises

1. Build a **PN-Counter** (supports decrement) using two G-Counters — one for increments, one for decrements; value is `inc.value() - dec.value()`.
2. Show your G-Counter merge is commutative by asserting `merge(a,b)` and `merge(b,a)` give the same counts dict.
3. Implement a **G-Set** (add-only set) whose merge is set union, and confirm it's idempotent.
4. Demonstrate the LWW data-loss problem: two concurrent writes at the same timestamp, and discuss how you'd break the tie deterministically (e.g. by node id).
5. Explain why idempotent merges make CRDTs safe under at-least-once message delivery.
