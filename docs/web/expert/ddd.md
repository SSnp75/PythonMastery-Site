---
title: Domain-Driven Design
description: Aggregates, bounded contexts, value objects, repositories and ubiquitous language
---

# Domain-Driven Design <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="clean-architecture/">Clean Architecture</a>, <a href="../proficient/orms/">ORMs</a></span>
  </div>
</div>

---

## Core concepts

DDD is a software design approach that focuses on the **business domain** — aligning code structure with how domain experts think.

| Concept | Definition | Python equivalent |
|---|---|---|
| **Entity** | Has identity (tracked by ID) | Class with `id` field |
| **Value Object** | Defined by attributes, no identity | `@dataclass(frozen=True)` |
| **Aggregate** | Cluster of entities with one root | Class that enforces invariants |
| **Repository** | Abstracts persistence | Protocol/ABC |
| **Domain Event** | Something meaningful happened | Dataclass representing the fact |
| **Bounded Context** | Boundary where a model applies | Separate module/package |
| **Ubiquitous Language** | Terms everyone agrees on | Method names match domain terms |

---

## Value Objects

No identity — defined entirely by their attributes:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int       # in cents to avoid floating point
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency not in ("USD", "EUR", "GBP"):
            raise ValueError(f"Unsupported currency: {self.currency}")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __str__(self):
        return f"${self.amount / 100:.2f} {self.currency}"


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

    def __post_init__(self):
        if not self.zip_code:
            raise ValueError("Zip code required")

    @property
    def full(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


# Value objects are equal if all attributes match
m1 = Money(1000, "USD")
m2 = Money(1000, "USD")
print(m1 == m2)   # True — same value, no identity

total = m1.add(m2)
print(total)   # $20.00 USD
```

---

## Entities

Have identity — two entities with same attributes but different IDs are different:

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Customer:
    id: UUID
    name: str
    email: str
    address: Address
    created_at: datetime = field(default_factory=datetime.utcnow)

    def change_address(self, new_address: Address) -> None:
        """Domain method — uses ubiquitous language."""
        self.address = new_address

    def change_email(self, new_email: str) -> None:
        if "@" not in new_email:
            raise ValueError("Invalid email")
        self.email = new_email

    def __eq__(self, other):
        """Entities are equal by ID, not attributes."""
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
```

---

## Aggregates

An aggregate is a **consistency boundary** — a cluster of entities and value objects with one root entity that enforces all invariants.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

@dataclass
class OrderLine:
    """Value object within the Order aggregate."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Money

    @property
    def total(self) -> Money:
        return self.unit_price.multiply(self.quantity)


@dataclass
class Order:
    """Aggregate root — all access to order lines goes through here."""
    id: UUID
    customer_id: UUID
    lines: list[OrderLine] = field(default_factory=list)
    status: str = "draft"
    placed_at: Optional[datetime] = None

    # ─── Domain invariants enforced here ─────────
    def add_line(self, product_id: UUID, name: str, qty: int, price: Money) -> None:
        if self.status != "draft":
            raise ValueError("Cannot modify a placed order")
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        # Check if product already in order
        for line in self.lines:
            if line.product_id == product_id:
                raise ValueError(f"Product {name} already in order. Update quantity instead.")

        self.lines.append(OrderLine(product_id, name, qty, price))

    def remove_line(self, product_id: UUID) -> None:
        if self.status != "draft":
            raise ValueError("Cannot modify a placed order")
        self.lines = [l for l in self.lines if l.product_id != product_id]

    def place(self) -> list:
        """Transition to placed — returns domain events."""
        if not self.lines:
            raise ValueError("Cannot place empty order")
        if self.status != "draft":
            raise ValueError(f"Cannot place order in status '{self.status}'")

        self.status = "placed"
        self.placed_at = datetime.utcnow()

        return [OrderPlaced(
            order_id=self.id,
            customer_id=self.customer_id,
            total=self.total,
            occurred_at=self.placed_at,
        )]

    def cancel(self) -> list:
        if self.status not in ("draft", "placed"):
            raise ValueError(f"Cannot cancel order in status '{self.status}'")
        self.status = "cancelled"
        return [OrderCancelled(order_id=self.id, occurred_at=datetime.utcnow())]

    @property
    def total(self) -> Money:
        if not self.lines:
            return Money(0, "USD")
        totals = [line.total for line in self.lines]
        result = totals[0]
        for t in totals[1:]:
            result = result.add(t)
        return result

    @property
    def line_count(self) -> int:
        return len(self.lines)
```

---

## Domain Events

Events represent **facts** — things that already happened:

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class OrderPlaced:
    order_id: UUID
    customer_id: UUID
    total: Money
    occurred_at: datetime

@dataclass(frozen=True)
class OrderCancelled:
    order_id: UUID
    occurred_at: datetime

@dataclass(frozen=True)
class PaymentReceived:
    order_id: UUID
    amount: Money
    payment_method: str
    occurred_at: datetime
```

Events are consumed by other parts of the system:

```python
class OrderEventHandler:
    def __init__(self, email_service, inventory_service):
        self.email = email_service
        self.inventory = inventory_service

    async def handle(self, event):
        if isinstance(event, OrderPlaced):
            await self.email.send_order_confirmation(event.order_id)
            await self.inventory.reserve_items(event.order_id)
        elif isinstance(event, OrderCancelled):
            await self.inventory.release_items(event.order_id)
```

---

## Repository Pattern

Repositories abstract persistence — the domain doesn't know about databases:

```python
from typing import Protocol
from uuid import UUID

class OrderRepository(Protocol):
    async def get(self, order_id: UUID) -> Order | None: ...
    async def save(self, order: Order) -> None: ...
    async def delete(self, order_id: UUID) -> None: ...
    async def find_by_customer(self, customer_id: UUID) -> list[Order]: ...

# SQLAlchemy implementation
class SQLAlchemyOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, order_id: UUID) -> Order | None:
        model = await self.session.get(OrderModel, str(order_id))
        return self._to_domain(model) if model else None

    async def save(self, order: Order) -> None:
        model = self._to_model(order)
        self.session.merge(model)
        await self.session.flush()

    def _to_domain(self, model: OrderModel) -> Order:
        """Convert database model to domain aggregate."""
        lines = [
            OrderLine(
                product_id=UUID(l.product_id),
                product_name=l.product_name,
                quantity=l.quantity,
                unit_price=Money(l.unit_price_cents, l.currency),
            )
            for l in model.lines
        ]
        return Order(
            id=UUID(model.id),
            customer_id=UUID(model.customer_id),
            lines=lines,
            status=model.status,
            placed_at=model.placed_at,
        )
```

---

## Bounded Contexts

Each context has its own model of the same real-world concept:

```python
# ─── Catalog Context ──────────────
# "Product" here means: name, description, images, categories, price

@dataclass
class Product:       # catalog context
    id: UUID
    name: str
    description: str
    price: Money
    images: list[str]
    categories: list[str]

# ─── Order Context ────────────────
# "Product" here means: just an ID, name, and price (snapshot at order time)

@dataclass(frozen=True)
class OrderLine:     # order context
    product_id: UUID
    product_name: str        # snapshot — doesn't change if catalog updates
    unit_price: Money        # snapshot — price at time of order

# ─── Shipping Context ─────────────
# "Product" here means: weight and dimensions

@dataclass
class ShippableItem:   # shipping context
    product_id: UUID
    weight_kg: float
    dimensions_cm: tuple[float, float, float]
```

These are **different models of the same thing** in different contexts. They communicate via events, not shared databases.

---

## Use Case (Application Service)

```python
class PlaceOrder:
    def __init__(self, order_repo: OrderRepository, event_bus: EventPublisher):
        self.order_repo = order_repo
        self.event_bus = event_bus

    async def execute(self, order_id: UUID) -> None:
        order = await self.order_repo.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)

        # Domain logic lives in the aggregate
        events = order.place()

        # Persist
        await self.order_repo.save(order)

        # Publish events
        for event in events:
            await self.event_bus.publish(event)
```

---

## Practice Exercises

1. **Model a banking domain** with Account (aggregate), Transaction (entity), Money (value object) and events.
2. **Implement the Order aggregate** above with full test coverage (no database).
3. **Design bounded contexts** for an e-commerce platform: Catalog, Orders, Payments, Shipping.
4. **Write a repository** that maps between domain entities and SQLAlchemy models.
5. **Implement event-driven communication** between two bounded contexts.
6. **Apply ubiquitous language** — review a codebase and rename methods/classes to match how domain experts talk.
