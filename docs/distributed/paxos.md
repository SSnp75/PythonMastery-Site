---
title: "Paxos"
description: The Paxos consensus family — proposers, acceptors and quorum agreement
---

# Paxos <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="raft/">Raft</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What Paxos achieves and why it's famous
- [x] The roles: proposer, acceptor, learner
- [x] The two-phase protocol (prepare, accept)
- [x] Why quorum overlap guarantees safety
- [x] Paxos vs Raft, and when you'd meet each

---

## The most famous consensus algorithm

**Paxos** (Leslie Lamport, 1998) solves the same problem as [Raft](raft.md) — getting unreliable machines to agree on a single value despite crashes and message loss — and it's the algorithm that proved consensus is *possible* under those conditions. It underpins Google's Chubby, Spanner, and many other foundational systems.

Paxos is also famous for being **hard to understand** — Raft was created specifically as a more approachable alternative. We'll build the intuition and prove the key safety property with runnable code, without drowning in the full protocol.

---

## The roles

- **Proposer** — proposes a value and drives the agreement.
- **Acceptor** — votes on proposals; a *majority* of acceptors deciding makes a value chosen.
- **Learner** — learns the chosen value (often the same nodes play multiple roles).

Agreement is reached when a **majority (quorum)** of acceptors accept the same proposal — the same quorum idea as Raft.

---

## The two-phase protocol

Paxos reaches agreement in two round-trips, using monotonically increasing **proposal numbers**:

```
   Phase 1 — PREPARE(n)
     proposer → acceptors: "will you consider proposal n?"
     acceptors → proposer: "yes, and here's any value I already accepted"
                           (only if n is the highest they've seen)

   Phase 2 — ACCEPT(n, value)
     proposer → acceptors: "accept value for proposal n"
     acceptors → proposer: "accepted" (unless they promised a higher n meanwhile)

   → once a majority accept, the value is CHOSEN
```

The subtle, brilliant part: in Phase 1, if any acceptor reports a value it already accepted, the proposer **must reuse that value** instead of its own. This is what prevents two different values from ever being chosen — a proposer with a higher number "inherits" any value that might already be chosen.

---

## Why quorum overlap makes it safe

Safety rests on one fact: **any two majorities of the same set must share at least one member.** That overlapping acceptor "remembers" the earlier decision and forces later proposals to respect it. The quorum logic is identical to Raft's:

```python
def has_majority(votes: int, cluster_size: int) -> bool:
    return votes > cluster_size // 2
```

```python
print(has_majority(3, 5))   # True  — 3 of 5 is a majority
print(has_majority(2, 5))   # False
# Two majorities of 5 must overlap:
#   {A,B,C} and {C,D,E} share C  → C carries the earlier decision forward
```

Output:

```text
True
False
```

Because every majority of a 5-node cluster contains at least one of any other majority's members, no two conflicting values can both gather a majority without some acceptor contradicting itself — which the protocol forbids. That overlap is the entire safety guarantee, and it's why (like Raft) Paxos uses odd cluster sizes.

!!! note "This shows the safety intuition, not full Paxos"
    Implementing correct Paxos (especially Multi-Paxos, which chains single-decree Paxos to agree on a *log* of values) is genuinely intricate — proposal-number handling, the value-inheritance rule, and liveness under dueling proposers all have sharp edges. The quorum-overlap property above is the heart of *why* it's safe; the full protocol is what makes it work in practice.

---

## Multi-Paxos and variants

Basic ("single-decree") Paxos agrees on *one* value. Real systems need agreement on an ordered *sequence* (a replicated log), so they use **Multi-Paxos**: elect a stable leader to skip Phase 1 on every entry, then run only Phase 2 repeatedly. At that point it looks a lot like Raft — which is not a coincidence.

Notable variants: **Fast Paxos** (fewer round-trips), **EPaxos** (leaderless, for lower latency), **Cheap Paxos** (fewer acceptors).

---

## Paxos vs Raft

| | **Paxos** | **Raft** |
|---|---|---|
| Year / author | 1998, Lamport | 2014, Ongaro & Ousterhout |
| Design goal | Prove consensus is possible | Be *understandable* |
| Leader | Optional (Multi-Paxos adds one) | Central to the design |
| Reputation | Correct but hard to grasp/implement | Easier to learn and implement |
| Used in | Chubby, Spanner, Megastore | etcd, Consul, CockroachDB |

**Which will you meet?** You'll rarely implement either from scratch. You'll *use* systems built on them — Spanner/Chubby (Paxos) or etcd/Consul (Raft). Learn Raft first for intuition; understand Paxos to appreciate the foundations and to read the literature. They solve the same problem with the same core insight (quorum overlap); Raft just packages it more accessibly.

---

## Practice exercises

1. Enumerate all 3-node majorities (`{A,B}, {A,C}, {B,C}`) and confirm every pair overlaps — the safety property by hand.
2. Explain in your own words why a proposer must adopt a previously-accepted value it learns about in Phase 1.
3. Describe a "dueling proposers" scenario where two proposers keep pre-empting each other, and how a stable leader (Multi-Paxos) fixes it.
4. Compare the message flow of Multi-Paxos (steady state) with Raft's `AppendEntries` and note the similarity.
5. Given a system requirement, decide whether you'd reach for an etcd (Raft) or a Spanner-like (Paxos) solution, and justify it.
