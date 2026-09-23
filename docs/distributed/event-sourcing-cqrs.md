---
title: "Event Sourcing & CQRS"
description: Model state as an immutable log of events and separate reads from writes
---

# Event Sourcing & CQRS <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../web/expert/event-driven-architecture/">Event-driven Architecture</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Store state as a log of events, not a current snapshot
- [x] Rebuild state by replaying events
- [x] Use snapshots to speed up replay
- [x] Separate reads from writes with CQRS
- [x] The tradeoffs of both patterns

---

## Event sourcing: the log is the truth

Traditional apps store the **current state** — a `balance` column that you overwrite. Event sourcing stores the **sequence of changes** instead: every deposit and withdrawal as an immutable event. The current state is *derived* by replaying the log.

```
   Traditional:  balance = 100   (overwritten each change; history lost)

   Event-sourced: [Deposited(100), Withdrawn(30), Deposited(50), Withdrawn(20)]
                   → replay → balance = 100   (full history kept)
```

You never update or delete; you only **append** new events. The log becomes a complete, auditable history of everything that ever happened.

---

## Rebuilding state from events

The core mechanic: start from empty, apply each event in order. Fully runnable:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Deposited:
    amount: int

@dataclass(frozen=True)
class Withdrawn:
    amount: int

class Account:
    def __init__(self) -> None:
        self.balance = 0

    def apply(self, event) -> None:
        if isinstance(event, Deposited):
            self.balance += event.amount
        elif isinstance(event, Withdrawn):
            self.balance -= event.amount
```

Replaying a log to reconstruct the current balance:

```python
event_log = [Deposited(100), Withdrawn(30), Deposited(50), Withdrawn(20)]

account = Account()
for event in event_log:
    account.apply(event)

print("rebuilt balance:", account.balance)
```

Output:

```text
rebuilt balance: 100
```

The balance (100) is *computed* from the events, never stored directly. Replay is **deterministic** — run it again on the same log and you always get 100. This is the superpower of event sourcing: given the log, you can reconstruct the state at *any* point in time (audit), debug by replaying, or build entirely new views from the same events.

---

## Why this is powerful

- **Complete audit trail.** Every change is recorded with its cause — invaluable for finance, compliance, debugging. You can answer "how did we get to this state?"
- **Time travel.** Replay up to any point to see historical state.
- **Rebuild/repair.** Fix a bug in how state is derived, then rebuild by replaying — the events are untouched.
- **New views for free.** Want a new report? Replay the existing events into a new projection; no need to have captured it up front.

---

## Snapshots: don't replay millions of events

Replaying from the beginning gets slow once a log has millions of events. The fix is **snapshots**: periodically save the derived state plus the log position, then replay only the events *after* the snapshot.

```python
@dataclass
class Snapshot:
    balance: int
    version: int          # index of the last event included

def rebuild(events: list, snapshot: Snapshot | None = None) -> int:
    account = Account()
    start = 0
    if snapshot is not None:
        account.balance = snapshot.balance
        start = snapshot.version + 1       # skip events already in the snapshot
    for event in events[start:]:
        account.apply(event)
    return account.balance

# snapshot after the first two events (balance 70), replay only the rest
snap = Snapshot(balance=70, version=1)
print(rebuild(event_log, snap))            # -> 100
```

Snapshots trade a little storage for much faster reconstruction — replay 100 recent events instead of 10 million.

---

## CQRS: separate reads from writes

**CQRS** (Command Query Responsibility Segregation) splits the model in two: **commands** (writes) go through one path, **queries** (reads) through another. They can use different models, and even different databases, each optimized for its job.

```
   Command (write)                     Query (read)
   ─────────────                       ────────────
   DepositMoney  ──▶ append event ──▶  read model / projection ──▶ GetBalance
                     (event store)      (fast, denormalized view)
```

Event sourcing and CQRS pair naturally: **commands append events; events update read-optimized projections** that queries hit. The write side stays a clean append-only log; the read side is whatever shape makes queries fast (a denormalized table, a search index, a cache).

- **Command side** — validates and appends events. Normalized, consistency-focused.
- **Query side** — one or more *projections* built by consuming events. Denormalized, read-optimized, possibly many different views of the same events.

They're often (not always) used together. You can do CQRS without event sourcing (just separate read/write models), and event sourcing without CQRS (replay for reads too, if volume is low).

---

## The honest tradeoffs

**Gains:** full audit history, time travel, rebuildable state, flexible read models, natural fit with [event-driven](../web/expert/event-driven-architecture.md) and distributed systems.

**Costs:**

- **Complexity.** Far more moving parts than a CRUD table. Don't reach for it unless the audit/history/scale needs justify it.
- **Eventual consistency.** With CQRS, the read projection lags the write — a query right after a command may not see the change yet. The UI must tolerate this.
- **Schema evolution.** Events are stored forever, so old event formats must remain readable as your code changes (versioned events, upcasters).
- **Querying is different.** You can't just `SELECT` current state from the event log — you need projections.

!!! warning "Event sourcing is not a default"
    It's a specialized pattern for domains where history, audit, or complex read/write scaling genuinely matter (finance, ordering, logistics). For a typical CRUD app, a normal database with an audit log is simpler and enough. Adopt event sourcing deliberately, per bounded context — not blanket across a whole system.

---

## Practice exercises

1. Add a `Transferred(from_amount, to_amount)` event and handle it in `apply`; replay a log containing it.
2. Add validation on the command side: reject a `Withdrawn` that would make the balance negative *before* appending the event.
3. Build a projection that produces a *transaction count* view from the same event log (a second read model).
4. Implement automatic snapshotting: create a snapshot every N events and use it in `rebuild`.
5. Explain a concrete scenario where the read model being briefly stale (CQRS eventual consistency) is acceptable, and one where it isn't.
