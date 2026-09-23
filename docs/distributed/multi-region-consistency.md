---
title: "Multi-region Consistency"
description: Consistency across geo-distributed regions — replication, conflicts and causality
---

# Multi-region Consistency <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="crdts/">CRDTs</a>, <a href="index/">Distributed Systems intro</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why geography forces consistency tradeoffs
- [x] The strong vs eventual consistency spectrum
- [x] Resolve write conflicts (LWW with tie-breaks)
- [x] Track causality with vector clocks
- [x] Choose a consistency model per use case

---

## Why regions change everything

When your data lives in one datacenter, coordination is cheap. Spread it across continents — US, Europe, Asia — and physics intervenes: a round trip between regions is 100–300 ms. If every write had to synchronously reach every region, writes would crawl. So you replicate **asynchronously**, which means regions can temporarily disagree, and two regions can accept **conflicting writes** to the same key at the same time.

```
   us-west  ──write "blue"──┐          ┌── how do these reconcile
                            ├─ sync ───┤   when they meet?
   us-east  ──write "red"───┘          └──
```

This is the [CAP theorem](index.md) made concrete: during a network partition you must choose **consistency** (reject writes until healed) or **availability** (accept writes and reconcile later). Multi-region systems usually lean toward availability, which makes **conflict resolution** the central problem.

---

## The consistency spectrum

| Model | Guarantee | Cost |
|---|---|---|
| **Strong** | Every read sees the latest write, everywhere | Slow cross-region coordination (consensus) |
| **Read-your-writes** | You see your own writes; others may lag | Moderate |
| **Eventual** | Replicas converge *eventually* if writes stop | Fast, but reads can be stale |

There's no free lunch: stronger consistency costs latency and availability. The skill is picking the *weakest* model your use case can tolerate — a bank balance needs strong; a "like" count is fine eventually consistent.

---

## Resolving conflicts: LWW with a deterministic tie-break

The simplest conflict resolution is **last-write-wins** by timestamp. But two regions can produce the *same* timestamp — so you need a deterministic tie-breaker (like region name) so **every** replica independently picks the same winner. Runnable:

```python
from dataclasses import dataclass

@dataclass
class Versioned:
    value: str
    ts: float
    region: str          # tie-breaker when timestamps are equal

def resolve(a: Versioned, b: Versioned) -> Versioned:
    if a.ts != b.ts:
        return a if a.ts > b.ts else b
    return a if a.region > b.region else b   # deterministic on equal timestamps
```

```python
west = Versioned("blue", ts=100.0, region="us-west")
east = Versioned("red",  ts=100.0, region="us-east")   # same timestamp!

winner = resolve(west, east)
print("winner:", winner.value, "from", winner.region)
```

Output:

```text
winner: blue from us-west
```

With identical timestamps, the tie-break by region name picks `us-west` (since `"us-west" > "us-east"`) — and crucially, *every* replica computes the same winner, so they converge. Without a deterministic tie-break, two regions could each pick a different "winner" and never agree.

!!! warning "LWW silently discards the losing write"
    Whoever loses the timestamp comparison is *gone*. That's acceptable for a preference or a cache, but not for anything where every update must survive (inventory, financial transactions). For those, use a [CRDT](crdts.md) that merges without loss, or require strong consistency. LWW also trusts clocks — clock skew across regions can crown the wrong winner.

---

## Tracking causality with vector clocks

Wall-clock timestamps can't tell whether two writes were *causally related* (one saw the other) or truly *concurrent*. **Vector clocks** — a counter per node — capture this. Runnable:

```python
def happens_before(a: dict, b: dict) -> bool:
    """True if event a causally precedes b."""
    keys = set(a) | set(b)
    le = all(a.get(k, 0) <= b.get(k, 0) for k in keys)
    lt = any(a.get(k, 0) <  b.get(k, 0) for k in keys)
    return le and lt

def concurrent(a: dict, b: dict) -> bool:
    return not happens_before(a, b) and not happens_before(b, a) and a != b
```

```python
a = {"west": 2, "east": 1}
b = {"west": 3, "east": 1}    # b saw everything a did, plus one more west event
c = {"west": 2, "east": 2}    # c diverged from b

print("a happens-before b:", happens_before(a, b))   # True — b descends from a
print("b concurrent with c:", concurrent(b, c))      # True — neither precedes the other
```

Output:

```text
a happens-before b: True
b concurrent with c: True
```

`a → b` because `b`'s vector dominates `a`'s (it saw everything and more). But `b` and `c` are **concurrent** — each has an event the other didn't see, so neither caused the other. That's exactly the case a system must flag as a genuine conflict needing resolution (or a CRDT merge), versus a simple overwrite. Vector clocks let you distinguish "this update supersedes that one" from "these two truly clash."

---

## Strategies in practice

- **Single-writer region (leader per key).** Route all writes for a key to one "home" region; other regions read a replica. Avoids write conflicts entirely, at the cost of cross-region write latency for non-home regions.
- **Multi-writer + conflict resolution.** Accept writes anywhere, reconcile with LWW, vector clocks, or CRDTs. Best availability, needs careful conflict handling.
- **Strong consistency via consensus.** Run [Raft](raft.md)/Paxos across regions for the data that truly needs it — accept the latency.
- **CRDTs.** For data that fits their model ([CRDTs](crdts.md)), get conflict-free multi-region writes with no coordination — the cleanest option where applicable.

!!! tip "Segment your data by consistency need"
    Don't pick one model for everything. Put the few things that need strong consistency (payments, balances) behind consensus, and let the rest (profiles, counters, activity feeds) be eventually consistent. This is how large systems get both correctness *and* low latency.

---

## Practice exercises

1. Extend `resolve` to also record which write lost, so you can log/audit discarded conflicting writes.
2. Implement vector-clock `merge` (element-wise max) and `increment`, then show a causal chain of three events.
3. Construct two vector clocks that are concurrent and explain, in terms of events, why neither happened-before the other.
4. Design consistency choices for a social app: which data is strong, read-your-writes, or eventual, and why.
5. Explain why LWW needs a deterministic tie-breaker for replicas to converge, with a concrete equal-timestamp example.
