---
title: Microservices Patterns
description: Saga, event sourcing, CQRS, outbox pattern and distributed transactions
---

# Microservices Patterns <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="distributed-theory/">Distributed Systems Theory</a></span>
  </div>
</div>

---

## Event Sourcing

Instead of storing current state, store all **events** that led to the current state.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

# ─── Events (immutable facts) ─────────────────────
@dataclass(frozen=True)
class AccountCreated:
    account_id: str
    owner: str
    occurred_at: datetime

@dataclass(frozen=True)
class MoneyDeposited:
    account_id: str
    amount: int      # cents
    occurred_at: datetime

@dataclass(frozen=True)
class MoneyWithdrawn:
    account_id: str
    amount: int
    occurred_at: datetime

# ─── Aggregate (rebuilt from events) ──────────────
class BankAccount:
    def __init__(self):
        self.id = None
        self.owner = None
        self.balance = 0
        self._events: list = []

    def apply(self, event):
        """Apply event to update state."""
        if isinstance(event, AccountCreated):
            self.id = event.account_id
            self.owner = event.owner
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
        self._events.append(event)

    @classmethod
    def from_events(cls, events: list) -> "BankAccount":
        """Rebuild state from event history."""
        account = cls()
        for event in events:
            account.apply(event)
        return account

    # Commands (produce events)
    def deposit(self, amount: int) -> MoneyDeposited:
        event = MoneyDeposited(self.id, amount, datetime.utcnow())
        self.apply(event)
        return event

    def withdraw(self, amount: int) -> MoneyWithdrawn:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        event = MoneyWithdrawn(self.id, amount, datetime.utcnow())
        self.apply(event)
        return event

# Usage
events = [
    AccountCreated("acc-1", "Alice", datetime.utcnow()),
    MoneyDeposited("acc-1", 10000, datetime.utcnow()),
    MoneyDeposited("acc-1", 5000, datetime.utcnow()),
    MoneyWithdrawn("acc-1", 3000, datetime.utcnow()),
]

account = BankAccount.from_events(events)
print(f"Balance: ${account.balance / 100:.2f}")   # $120.00
```

### Benefits of Event Sourcing:
- Complete audit trail (every change recorded)
- Time travel (rebuild state at any point)
- Event replay (fix bugs, reprocess)
- Natural fit for CQRS

---

## CQRS (Command Query Responsibility Segregation)

Separate the **write model** (commands) from the **read model** (queries):

```python
# ─── Write side (commands) ────────────────────────
class OrderCommandHandler:
    def __init__(self, event_store, event_bus):
        self.event_store = event_store
        self.event_bus = event_bus

    async def handle_place_order(self, cmd):
        # Load aggregate from events
        events = await self.event_store.load(cmd.order_id)
        order = Order.from_events(events)

        # Execute business logic
        new_events = order.place()

        # Save new events
        await self.event_store.append(cmd.order_id, new_events)

        # Publish for read side to consume
        for event in new_events:
            await self.event_bus.publish(event)

# ─── Read side (queries) ──────────────────────────
class OrderReadModel:
    """Denormalized view optimized for reading."""

    def __init__(self, db):
        self.db = db

    async def handle_event(self, event):
        """Update read model when events occur."""
        if isinstance(event, OrderPlaced):
            await self.db.execute("""
                INSERT INTO order_summary (id, customer, total, status, placed_at)
                VALUES (?, ?, ?, 'placed', ?)
            """, (event.order_id, event.customer_id, event.total, event.occurred_at))

    async def get_orders_by_customer(self, customer_id):
        """Fast read — no joins, no aggregation."""
        return await self.db.fetch_all(
            "SELECT * FROM order_summary WHERE customer = ? ORDER BY placed_at DESC",
            (customer_id,),
        )
```

---

## Outbox Pattern (reliable event publishing)

Ensure events are published **exactly once** even if the service crashes:

```python
async def place_order(session, order_data):
    """Write order AND outbox event in same transaction."""
    # Both in one transaction — atomic!
    order = Order(**order_data)
    session.add(order)

    # Write to outbox table (same DB, same transaction)
    outbox_event = OutboxEvent(
        aggregate_id=order.id,
        event_type="order.placed",
        payload=json.dumps(order.to_dict()),
    )
    session.add(outbox_event)

    await session.commit()
    # Event is guaranteed to be in outbox if order was saved

# Separate process polls outbox and publishes
async def outbox_publisher():
    while True:
        events = await db.fetch("SELECT * FROM outbox WHERE published = FALSE LIMIT 100")
        for event in events:
            await message_broker.publish(event.event_type, event.payload)
            await db.execute("UPDATE outbox SET published = TRUE WHERE id = ?", (event.id,))
        await asyncio.sleep(1)
```

---

## Saga Pattern (distributed transactions)

When an operation spans multiple services, use compensating transactions:

```python
@dataclass
class SagaStep:
    name: str
    action: callable      # forward action
    compensation: callable  # rollback action

class Saga:
    def __init__(self, steps: list[SagaStep]):
        self.steps = steps
        self.completed: list[SagaStep] = []

    async def execute(self, context: dict):
        for step in self.steps:
            try:
                await step.action(context)
                self.completed.append(step)
            except Exception as e:
                print(f"  Step '{step.name}' failed: {e}")
                await self.compensate(context)
                raise

    async def compensate(self, context: dict):
        """Run compensating transactions in reverse order."""
        for step in reversed(self.completed):
            try:
                await step.compensation(context)
                print(f"  Compensated: {step.name}")
            except Exception as e:
                print(f"  COMPENSATION FAILED for {step.name}: {e}")
                # Log for manual intervention!

# Usage
order_saga = Saga([
    SagaStep("reserve_inventory", reserve_stock, release_stock),
    SagaStep("charge_payment", charge_card, refund_card),
    SagaStep("create_shipment", create_shipment, cancel_shipment),
    SagaStep("send_confirmation", send_email, lambda ctx: None),
])

await order_saga.execute({"order_id": "123", "amount": 9999})
```

---

## Practice Exercises

1. **Implement event sourcing** for a shopping cart (add item, remove item, checkout).
2. **Build a CQRS system** with separate write and read models for a blog.
3. **Implement the outbox pattern** with PostgreSQL and a background publisher.
4. **Build a Saga** for a 4-step booking process (hotel + flight + car + payment).
5. **Implement event replay** — rebuild read model from scratch by replaying all events.
6. **Add snapshotting** to event sourcing to avoid replaying entire event history.
