---
title: Distributed Systems Theory
description: CAP theorem, consistency models, Raft consensus, vector clocks and partition handling
---

# Distributed Systems Theory <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
  </div>
</div>

---

## CAP Theorem

In a distributed system with network partitions, you can guarantee at most **two of three**:

- **C**onsistency — every read returns the most recent write
- **A**vailability — every request gets a response (not an error)
- **P**artition tolerance — system works despite network failures

Since network partitions **always happen**, the real choice is: **CP** or **AP**.

| System | Choice | Behavior during partition |
|---|---|---|
| PostgreSQL (single node) | CA | Not distributed — no partitions |
| ZooKeeper, etcd | CP | Rejects writes if no quorum |
| Cassandra, DynamoDB | AP | Accepts writes, reconciles later |
| MongoDB | Configurable | Depends on read/write concern |

---

## Consistency models

From strongest to weakest:

```
Linearizability (strongest)
  │  Every read sees the most recent write globally
  ▼
Sequential consistency
  │  Operations appear in some global order consistent with program order
  ▼
Causal consistency
  │  Causally related operations seen in order; concurrent ops may differ
  ▼
Eventual consistency (weakest)
     All replicas converge eventually; no ordering guarantees
```

---

## Raft consensus algorithm (simplified Python)

```python
from enum import Enum
from dataclasses import dataclass, field
import random

class Role(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    command: str

@dataclass
class RaftNode:
    node_id: int
    role: Role = Role.FOLLOWER
    current_term: int = 0
    voted_for: int | None = None
    log: list[LogEntry] = field(default_factory=list)
    commit_index: int = -1
    leader_id: int | None = None

    def start_election(self):
        """Candidate requests votes from other nodes."""
        self.role = Role.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        # In real implementation: send RequestVote RPCs to all nodes
        print(f"  Node {self.node_id}: starting election for term {self.current_term}")

    def receive_vote_request(self, candidate_id: int, candidate_term: int) -> bool:
        """Decide whether to vote for a candidate."""
        if candidate_term < self.current_term:
            return False
        if candidate_term > self.current_term:
            self.current_term = candidate_term
            self.role = Role.FOLLOWER
        if self.voted_for is None or self.voted_for == candidate_id:
            self.voted_for = candidate_id
            return True
        return False

    def become_leader(self):
        """Won election — become leader."""
        self.role = Role.LEADER
        self.leader_id = self.node_id
        print(f"  Node {self.node_id}: became LEADER for term {self.current_term}")

    def append_entry(self, command: str):
        """Leader appends entry to log, replicates to followers."""
        if self.role != Role.LEADER:
            raise ValueError("Only leader can append entries")
        entry = LogEntry(term=self.current_term, command=command)
        self.log.append(entry)
        # In real implementation: send AppendEntries RPCs to followers
        # Commit when majority acknowledges
        print(f"  Leader: appending '{command}' (log size: {len(self.log)})")
```

---

## Vector clocks — tracking causality

```python
from collections import defaultdict

class VectorClock:
    """Track causal ordering of events in a distributed system."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock: dict[str, int] = defaultdict(int)

    def increment(self):
        """Called when this node performs a local event."""
        self.clock[self.node_id] += 1
        return dict(self.clock)

    def update(self, other_clock: dict[str, int]):
        """Called when receiving a message — merge clocks."""
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock[node], time)
        self.clock[self.node_id] += 1

    def is_before(self, other: "VectorClock") -> bool:
        """Returns True if self happened-before other."""
        return (
            all(self.clock.get(k, 0) <= other.clock.get(k, 0) for k in self.clock) and
            self.clock != other.clock
        )

    def is_concurrent(self, other: "VectorClock") -> bool:
        """Returns True if events are concurrent (no causal relationship)."""
        return not self.is_before(other) and not other.is_before(self)

# Usage
a = VectorClock("A")
b = VectorClock("B")

a.increment()       # A: {A:1}
a.increment()       # A: {A:2}

# A sends message to B
b.update(a.clock)   # B: {A:2, B:1}
b.increment()       # B: {A:2, B:2}

# Detect concurrent events
a.increment()       # A: {A:3}
print(a.is_concurrent(b))   # True — A:3 and B:2 are concurrent
```

---

## Conflict resolution strategies

| Strategy | How | When to use |
|---|---|---|
| Last-Writer-Wins (LWW) | Highest timestamp wins | Simple, acceptable data loss |
| Multi-Value (siblings) | Keep all conflicting versions | Shopping carts, sets |
| CRDTs | Mathematically guaranteed merge | Counters, sets, registers |
| Application-level | Custom merge logic | Complex business rules |

### CRDT example: G-Counter (grow-only counter)

```python
class GCounter:
    """Grow-only counter — always mergeable without conflicts."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: dict[str, int] = defaultdict(int)

    def increment(self, amount: int = 1):
        self.counts[self.node_id] += amount

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter"):
        """Merge is commutative, associative, idempotent — CRDT property."""
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts[node], count)

# Two nodes increment independently
c1 = GCounter("node-1")
c2 = GCounter("node-2")

c1.increment(5)
c2.increment(3)

# After network reconnection — merge
c1.merge(c2)
c2.merge(c1)

print(c1.value())   # 8
print(c2.value())   # 8  (both agree!)
```

---

## Practice Exercises

1. **Implement a simple Raft** leader election with 3 nodes (simulated).
2. **Build a vector clock** system and demonstrate causal vs concurrent events.
3. **Implement a G-Counter and PN-Counter** CRDT.
4. **Simulate a network partition** — show how CP and AP systems behave differently.
5. **Build a distributed key-value store** with eventual consistency and conflict resolution.
6. **Implement a gossip protocol** for membership and failure detection.
