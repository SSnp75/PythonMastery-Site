---
title: "Raft"
description: The Raft consensus algorithm — leader election, log replication and safety
---

# Raft <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="index/">Distributed Systems intro</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What consensus is and why it's hard
- [x] Raft's three roles and leader election
- [x] How terms and majorities prevent split-brain
- [x] Log replication basics
- [x] Where Raft is used in practice

---

## The consensus problem

Multiple servers must agree on a single value (or an ordered sequence of commands) even though messages get delayed, servers crash, and networks partition. This is **distributed consensus**, and it's genuinely hard — the naive "just have everyone vote" breaks under failures and partitions.

**Raft** is a consensus algorithm designed to be *understandable* (its predecessor Paxos is notoriously hard to grasp — see [Paxos](paxos.md)). It powers the coordination layer of many real systems: etcd (Kubernetes' brain), Consul, CockroachDB, and TiKV.

Raft keeps a **replicated log** consistent across servers by electing one **leader** that all changes flow through.

```
        ┌── follower ──┐
   ─────┤   leader     ├─────   one leader; followers replicate its log
        └── follower ──┘
```

---

## Three roles

Every node is in one of three states at any time:

- **Follower** — passive; responds to the leader and to vote requests.
- **Candidate** — a follower that timed out waiting for a leader and is now campaigning for votes.
- **Leader** — handles all client writes and replicates them to followers. There's at most one per term.

---

## Terms and majorities

Two ideas make Raft safe:

**Terms** are logical time — a monotonically increasing number. Each election starts a new term. A node always adopts the highest term it sees, which lets it detect and reject stale leaders/candidates.

**Majority (quorum)** — a candidate becomes leader only with votes from a *majority* of the cluster. This is the key to preventing **split-brain** (two leaders): in a 5-node cluster you need 3 votes, and two different candidates can't both get 3 votes from the same 5 nodes.

```python
def has_majority(votes: int, cluster_size: int) -> bool:
    return votes > cluster_size // 2
```

```python
print("5-node cluster needs", 5 // 2 + 1, "votes to win")   # -> 3
print(has_majority(3, 5))    # True  — 3 of 5
print(has_majority(2, 5))    # False — 2 of 5 is not a majority
```

Output:

```text
5-node cluster needs 3 votes to win
True
False
```

Because any two majorities of the same cluster must overlap in at least one node, and each node votes once per term, **two candidates cannot both win the same term** — that's the mathematical guarantee against split-brain. It's also why Raft clusters use *odd* sizes (3, 5, 7): a 5-node cluster tolerates 2 failures, same as a 6-node one, so the extra node buys nothing.

---

## Voting logic

A node grants its vote based on the candidate's **term** and whether it has already voted this term. Runnable:

```python
from dataclasses import dataclass

@dataclass
class Node:
    node_id: str
    current_term: int = 0
    voted_for: str | None = None

    def request_vote(self, candidate: str, term: int) -> bool:
        if term < self.current_term:
            return False                    # candidate is stale — reject
        if term > self.current_term:        # newer term: adopt it, reset vote
            self.current_term = term
            self.voted_for = None
        if self.voted_for in (None, candidate):
            self.voted_for = candidate      # grant (once per term)
            return True
        return False                        # already voted someone else this term
```

```python
node = Node("follower")
print(node.request_vote("A", term=1))   # True  — grants to A
print(node.request_vote("B", term=1))   # False — same term, already voted A
print(node.request_vote("B", term=2))   # True  — new term, can vote again
print("term:", node.current_term, "voted_for:", node.voted_for)
```

Output:

```text
True
False
True
term: 2 voted_for: B
```

The node votes for A in term 1, refuses B in the *same* term (one vote per term — this is what prevents double-voting), but grants B in the newer term 2. Adopting the higher term and resetting `voted_for` is exactly how Raft lets a fresh election proceed after the old one failed.

!!! note "This models the vote rule, not full Raft"
    Real Raft adds a crucial extra check omitted here for clarity: a node only grants its vote if the candidate's *log* is at least as up-to-date as its own. That log-completeness rule guarantees a new leader never loses committed entries. The term/one-vote logic above is the correct core; production Raft layers log safety on top.

---

## Log replication (the leader's job)

Once elected, the leader is the single entry point for changes:

1. Client sends a command to the leader.
2. Leader appends it to its log and sends it to all followers (`AppendEntries`).
3. Once a **majority** have stored it, the leader marks it **committed** and applies it to its state machine.
4. Leader tells followers the new commit index; they apply it too.

Because entries commit only after a majority replicate them, a committed entry survives any minority of failures — and the log-completeness voting rule ensures the next leader already has every committed entry. Heartbeats (empty `AppendEntries`) keep followers from starting needless elections.

---

## Where Raft is used

- **etcd** — the consistent key-value store behind Kubernetes.
- **Consul** — service discovery and configuration.
- **CockroachDB, TiKV, YugabyteDB** — distributed SQL/KV, one Raft group per data range.

If you need strong consistency across replicas, you generally reach for a system that runs Raft rather than implementing it yourself — it's subtle enough that using a battle-tested implementation (or the `etcd`/Consul API) is the right call.

---

## Practice exercises

1. Extend `has_majority` into a function that returns how many failures a cluster of size N tolerates (`(N-1)//2`), and tabulate it for N = 3, 4, 5, 6, 7.
2. Add the log-completeness check to `request_vote`: only grant if `candidate_last_term`/`candidate_last_index` is at least as up-to-date as the voter's.
3. Simulate an election across 5 `Node` objects and confirm exactly one candidate can reach a majority in a given term.
4. Model a split vote (no candidate gets a majority) and show how bumping the term lets a new election resolve it.
5. Explain why Raft clusters use odd numbers of nodes, using the failure-tolerance formula.
