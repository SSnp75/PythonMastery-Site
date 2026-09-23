---
title: "Saga Pattern & Distributed Transactions"
description: Coordinate changes across services with sagas and compensating transactions
---

# Saga Pattern & Distributed Transactions <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../web/expert/microservices/">Microservices</a>, <a href="queues/">Distributed Queues</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why cross-service transactions are hard
- [x] Why two-phase commit falls short
- [x] The saga pattern and compensating transactions
- [x] Build an orchestrated saga that rolls back on failure
- [x] Orchestration vs choreography

---

## The problem: no shared transaction

In a single database, a transaction gives you all-or-nothing (**atomicity**): wrap several changes in `BEGIN … COMMIT`, and if anything fails, `ROLLBACK` undoes it all. But in [microservices](../web/expert/microservices.md), each service owns its *own* database. An order that must reserve stock, charge a card, and schedule shipping spans three services and three databases — there's no single transaction that covers them.

```
   order flow spans 3 services, 3 databases:

   [inventory db]   [payments db]   [shipping db]
        │                │               │
   reserve stock → charge card → schedule ship
        │                │               │
        └── if shipping fails, how do we undo the first two? ──┘
```

If the third step fails, you can't `ROLLBACK` the first two — they were committed in separate databases. You need a different approach.

---

## Why not two-phase commit (2PC)?

The classic answer is **two-phase commit**: a coordinator asks all participants to "prepare," and if all agree, tells them to "commit." It does provide atomicity across services — but it's largely avoided in modern microservices because:

- **It's blocking.** Participants hold locks while waiting for the coordinator's decision. A slow or crashed coordinator can freeze everyone.
- **Poor availability.** It's a **CP** choice (see the [CAP theorem](index.md)) — a partition can stall the whole transaction.
- **Tight coupling.** Every service must support the same 2PC protocol and stay available together.

For long-running, loosely-coupled service interactions, 2PC's locking and blocking are unacceptable. Enter the saga.

---

## The saga pattern

A **saga** breaks a distributed transaction into a sequence of **local** transactions, one per service. Each step commits independently. If a later step fails, the saga runs **compensating transactions** — explicit "undo" operations — for the steps already completed, in reverse order.

```
   forward:   reserve_stock → charge_card → ship_order ✗ (fails)
   compensate:              ← refund_card ← release_stock

   (undo the completed steps, in reverse)
```

The crucial mindset shift: there's no automatic rollback. **You** write the compensation for each step (refund the charge, release the reservation). A saga trades strict atomicity for *eventual* consistency — the system passes through intermediate states, then either fully completes or fully compensates.

---

## An orchestrated saga

In **orchestration**, a central coordinator runs the steps and triggers compensations on failure. Fully runnable:

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Step:
    name: str
    action: Callable[[], None]
    compensate: Callable[[], None]

class Saga:
    def __init__(self) -> None:
        self.steps: list[Step] = []

    def add(self, name, action, compensate) -> None:
        self.steps.append(Step(name, action, compensate))

    def execute(self) -> dict:
        completed: list[Step] = []
        try:
            for step in self.steps:
                step.action()
                completed.append(step)
            return {"status": "committed",
                    "completed": [s.name for s in completed]}
        except Exception as e:
            for step in reversed(completed):     # undo in REVERSE order
                step.compensate()
            return {"status": "aborted", "reason": str(e),
                    "compensated": [s.name for s in reversed(completed)]}
```

### Happy path — everything commits

```python
log = []
def step_fns(name, fail=False):
    def action():
        if fail:
            raise RuntimeError(f"{name} failed")
        log.append(f"do:{name}")
    def compensate():
        log.append(f"undo:{name}")
    return action, compensate

saga = Saga()
for name in ["reserve_stock", "charge_card", "ship_order"]:
    action, comp = step_fns(name)
    saga.add(name, action, comp)

print(saga.execute())
print(log)
```

Output:

```text
{'status': 'committed', 'completed': ['reserve_stock', 'charge_card', 'ship_order']}
['do:reserve_stock', 'do:charge_card', 'do:ship_order']
```

All three steps ran in order and committed. No compensation needed.

### Failure path — automatic rollback via compensation

Now make the last step fail:

```python
log.clear()
saga = Saga()
a1, c1 = step_fns("reserve_stock")
a2, c2 = step_fns("charge_card")
a3, c3 = step_fns("ship_order", fail=True)     # this one fails
saga.add("reserve_stock", a1, c1)
saga.add("charge_card", a2, c2)
saga.add("ship_order", a3, c3)

print(saga.execute())
print(log)
```

Output:

```text
{'status': 'aborted', 'reason': 'ship_order failed', 'compensated': ['charge_card', 'reserve_stock']}
['do:reserve_stock', 'do:charge_card', 'undo:charge_card', 'undo:reserve_stock']
```

`ship_order` failed before doing anything, so the saga compensates the two completed steps **in reverse order**: first `undo:charge_card` (refund), then `undo:reserve_stock` (release the reservation). The system ends up back in a consistent state — as if the order never happened — even though three separate databases were involved. Reverse order matters: you undo the most recent commit first, mirroring how a stack unwinds.

!!! warning "Compensations must be reliable and idempotent"
    A compensation can itself fail or be retried, so it must be **idempotent** (refunding twice shouldn't double-refund — see [Queues](queues.md)). And some actions can't truly be undone (an email was sent) — for those you compensate with a corrective action (send a cancellation email), not a literal reversal. Design each step's "undo" carefully; it's the hardest part of a saga.

---

## Orchestration vs choreography

Two ways to coordinate a saga:

| | **Orchestration** | **Choreography** |
|---|---|---|
| Control | A central coordinator directs each step (like above) | No coordinator; services react to each other's [events](../web/expert/event-driven-architecture.md) |
| Flow visibility | Explicit, easy to follow | Emergent, spread across services |
| Coupling | Coordinator knows all steps | Services only know their events |
| Best for | Complex flows needing clear control | Simple flows, maximum decoupling |

- **Orchestration** — one service owns the workflow and calls each participant, triggering compensations on failure. Easier to understand and debug; the coordinator is a single place to see the whole flow.
- **Choreography** — each service publishes events; others react. `OrderCreated` → payment service charges and emits `PaymentCompleted` → shipping reacts. No central brain, but the flow is implicit and harder to trace.

**Rule of thumb:** orchestration for complex, multi-step flows where you want clear control and visibility; choreography for simple flows where decoupling matters most. Real tools: **Temporal**, **Camunda/Zeebe**, and AWS **Step Functions** are orchestration engines that handle the durability, retries, and state persistence you'd otherwise build yourself.

---

## Practice exercises

1. Add a `refund` and `release` that actually mutate a fake balance/inventory, and assert the numbers return to their starting values after an aborted saga.
2. Make compensations idempotent: track which steps have been compensated so running compensation twice is safe.
3. Handle a *compensation* that fails — log it and continue compensating the rest (a real saga can't just give up mid-rollback).
4. Rewrite the 3-step flow as a **choreography** using the event bus from [Event-driven Architecture](../web/expert/event-driven-architecture.md).
5. Explain why a saga gives *eventual* consistency rather than the atomicity of a single-database transaction.
