---
title: Behavioral Patterns
description: Observer, Strategy, Command, State Machine, Chain of Responsibility and Iterator
---

# Behavioral Patterns <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🏗️ Design Patterns · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~5 days</span>
  </div>
</div>

---

## Observer — publish/subscribe

```python
from typing import Protocol, Any

class EventHandler(Protocol):
    def handle(self, event: str, data: Any) -> None: ...

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event: str, handler: EventHandler):
        self._handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: EventHandler):
        self._handlers.get(event, []).remove(handler)

    def publish(self, event: str, data: Any = None):
        for handler in self._handlers.get(event, []):
            handler.handle(event, data)

# Concrete handlers
class Logger:
    def handle(self, event, data):
        print(f"  [LOG] {event}: {data}")

class EmailNotifier:
    def handle(self, event, data):
        print(f"  [EMAIL] Sending notification about {event}")

class MetricsCollector:
    def handle(self, event, data):
        print(f"  [METRIC] {event} recorded")

# Usage
bus = EventBus()
bus.subscribe("user.registered", Logger())
bus.subscribe("user.registered", EmailNotifier())
bus.subscribe("order.placed", Logger())
bus.subscribe("order.placed", MetricsCollector())

bus.publish("user.registered", {"name": "Alice", "email": "a@b.com"})
# [LOG] user.registered: {'name': 'Alice', 'email': 'a@b.com'}
# [EMAIL] Sending notification about user.registered

bus.publish("order.placed", {"order_id": 123, "total": 99.99})
# [LOG] order.placed: {'order_id': 123, 'total': 99.99}
# [METRIC] order.placed recorded
```

---

## Strategy — swap algorithms at runtime

```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list) -> list: ...

class QuickSort:
    def sort(self, data: list) -> list:
        if len(data) <= 1: return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class MergeSort:
    def sort(self, data: list) -> list:
        if len(data) <= 1: return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)
    def _merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        return result + left[i:] + right[j:]

class TimSort:
    def sort(self, data: list) -> list:
        return sorted(data)   # Python's built-in is TimSort!

# Context — uses strategy
class DataProcessor:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def process(self, data: list) -> list:
        return self._strategy.sort(data)

# Usage — swap algorithms without changing client code
processor = DataProcessor(QuickSort())
result = processor.process([5, 2, 8, 1, 9])
print(result)   # [1, 2, 5, 8, 9]

processor.set_strategy(MergeSort())
result = processor.process([5, 2, 8, 1, 9])
print(result)   # [1, 2, 5, 8, 9]
```

### Pythonic strategy (just use functions):

```python
def process_data(data: list, sort_func=sorted) -> list:
    return sort_func(data)

# Pass any callable
process_data(data, sort_func=lambda x: sorted(x, reverse=True))
```

---

## Command — encapsulate actions as objects

```python
from dataclasses import dataclass
from typing import Protocol

class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...

@dataclass
class InsertText:
    document: list
    position: int
    text: str

    def execute(self):
        self.document.insert(self.position, self.text)

    def undo(self):
        self.document.pop(self.position)

@dataclass
class DeleteText:
    document: list
    position: int
    _deleted: str = ""

    def execute(self):
        self._deleted = self.document.pop(self.position)

    def undo(self):
        self.document.insert(self.position, self._deleted)

# Command history for undo/redo
class Editor:
    def __init__(self):
        self.document: list[str] = []
        self._history: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command):
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()

    def undo(self):
        if self._history:
            cmd = self._history.pop()
            cmd.undo()
            self._redo_stack.append(cmd)

    def redo(self):
        if self._redo_stack:
            cmd = self._redo_stack.pop()
            cmd.execute()
            self._history.append(cmd)

# Usage
editor = Editor()
editor.execute(InsertText(editor.document, 0, "Hello"))
editor.execute(InsertText(editor.document, 1, "World"))
print(editor.document)   # ['Hello', 'World']

editor.undo()
print(editor.document)   # ['Hello']

editor.redo()
print(editor.document)   # ['Hello', 'World']
```

---

## State Machine

```python
from enum import Enum, auto

class OrderState(Enum):
    DRAFT = auto()
    PLACED = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

class Order:
    # Valid transitions
    TRANSITIONS = {
        OrderState.DRAFT: [OrderState.PLACED, OrderState.CANCELLED],
        OrderState.PLACED: [OrderState.PAID, OrderState.CANCELLED],
        OrderState.PAID: [OrderState.SHIPPED, OrderState.CANCELLED],
        OrderState.SHIPPED: [OrderState.DELIVERED],
        OrderState.DELIVERED: [],
        OrderState.CANCELLED: [],
    }

    def __init__(self):
        self.state = OrderState.DRAFT
        self._history = [self.state]

    def transition(self, new_state: OrderState):
        allowed = self.TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            raise ValueError(
                f"Cannot transition from {self.state.name} to {new_state.name}. "
                f"Allowed: {[s.name for s in allowed]}"
            )
        self.state = new_state
        self._history.append(new_state)

    def place(self): self.transition(OrderState.PLACED)
    def pay(self): self.transition(OrderState.PAID)
    def ship(self): self.transition(OrderState.SHIPPED)
    def deliver(self): self.transition(OrderState.DELIVERED)
    def cancel(self): self.transition(OrderState.CANCELLED)

# Usage
order = Order()
order.place()
order.pay()
order.ship()
print(order.state)   # OrderState.SHIPPED
print(order._history)  # [DRAFT, PLACED, PAID, SHIPPED]

try:
    order.cancel()   # can't cancel after shipping!
except ValueError as e:
    print(e)   # Cannot transition from SHIPPED to CANCELLED...
```

---

## Chain of Responsibility

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Request:
    amount: float
    description: str
    approved: bool = False
    approver: str = ""

class Approver(ABC):
    def __init__(self, next_approver: "Approver | None" = None):
        self._next = next_approver

    @abstractmethod
    def can_approve(self, request: Request) -> bool: ...

    @abstractmethod
    def name(self) -> str: ...

    def handle(self, request: Request) -> Request:
        if self.can_approve(request):
            request.approved = True
            request.approver = self.name()
            return request
        elif self._next:
            return self._next.handle(request)
        else:
            request.approved = False
            return request

class TeamLead(Approver):
    def name(self): return "Team Lead"
    def can_approve(self, request): return request.amount <= 1000

class Manager(Approver):
    def name(self): return "Manager"
    def can_approve(self, request): return request.amount <= 10000

class Director(Approver):
    def name(self): return "Director"
    def can_approve(self, request): return request.amount <= 100000

# Build chain
chain = TeamLead(Manager(Director()))

# Small request — approved by Team Lead
r1 = chain.handle(Request(500, "Office supplies"))
print(f"${r1.amount}: {r1.approved} by {r1.approver}")   # True by Team Lead

# Medium — approved by Manager
r2 = chain.handle(Request(5000, "New laptops"))
print(f"${r2.amount}: {r2.approved} by {r2.approver}")   # True by Manager

# Large — approved by Director
r3 = chain.handle(Request(50000, "Server upgrade"))
print(f"${r3.amount}: {r3.approved} by {r3.approver}")   # True by Director

# Too large — nobody can approve
r4 = chain.handle(Request(500000, "New building"))
print(f"${r4.amount}: {r4.approved}")   # False
```

---

## Practice Exercises

1. **Build an event system** for a game — player events trigger UI updates, sound effects and achievements.
2. **Implement Strategy** for different pricing algorithms (flat, tiered, volume discount).
3. **Build an undo system** for a drawing application using Command pattern.
4. **Implement a state machine** for a traffic light (red → green → yellow → red) with timers.
5. **Build a middleware chain** (like Express.js) using Chain of Responsibility.
