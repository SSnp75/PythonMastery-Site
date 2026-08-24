---
title: Test-Driven Development
description: Red-green-refactor cycle, design benefits and TDD workflow
---

# Test-Driven Development <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="pytest/">pytest</a></span>
  </div>
</div>

---

## The TDD cycle

```
┌──────────────────────────────────────────────┐
│  1. RED    — Write a failing test            │
│  2. GREEN  — Write minimal code to pass      │
│  3. REFACTOR — Clean up, keep tests green    │
│  └───── Repeat ─────────────────────────────┘
```

Each cycle takes **1-5 minutes**. You always have working code.

---

## TDD walkthrough: building a Stack

### Cycle 1: push and peek

```python
# test_stack.py — Step 1: RED (write failing test)
import pytest
from stack import Stack

def test_new_stack_is_empty():
    s = Stack()
    assert s.is_empty()

def test_push_and_peek():
    s = Stack()
    s.push(42)
    assert s.peek() == 42
    assert not s.is_empty()
```

```bash
pytest   # FAILS — stack.py doesn't exist yet
```

```python
# stack.py — Step 2: GREEN (minimal code to pass)
class Stack:
    def __init__(self):
        self._items = []

    def is_empty(self):
        return len(self._items) == 0

    def push(self, item):
        self._items.append(item)

    def peek(self):
        return self._items[-1]
```

```bash
pytest   # PASSES ✓
```

### Cycle 2: pop

```python
# test_stack.py — add new failing test
def test_pop_returns_last_pushed():
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.is_empty()

def test_pop_empty_raises():
    s = Stack()
    with pytest.raises(IndexError, match="empty"):
        s.pop()
```

```python
# stack.py — add pop
def pop(self):
    if self.is_empty():
        raise IndexError("Cannot pop from empty stack")
    return self._items.pop()
```

### Cycle 3: size

```python
def test_size():
    s = Stack()
    assert len(s) == 0
    s.push("a")
    s.push("b")
    assert len(s) == 2
    s.pop()
    assert len(s) == 1
```

```python
def __len__(self):
    return len(self._items)
```

### Step 3: REFACTOR

After all tests pass, look for improvements:

```python
# Final clean version
class Stack:
    """A LIFO stack with O(1) push, pop and peek."""

    def __init__(self):
        self._items: list = []

    def push(self, item) -> None:
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("Cannot pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("Cannot peek empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"
```

Tests still pass after refactoring — confidence!

---

## TDD benefits

| Benefit | How |
|---|---|
| **Design feedback** | Hard-to-test code = bad design. TDD forces simple interfaces. |
| **Documentation** | Tests show how the code is meant to be used. |
| **Confidence** | Refactor freely — tests catch regressions instantly. |
| **Focus** | Write only the code needed to pass the test. No overengineering. |
| **Regression safety** | Every bug gets a test before the fix. Never breaks again. |

---

## TDD anti-patterns to avoid

!!! warning "Don't do these"

    - **Testing implementation details** — test behavior, not internal state
    - **Writing too many tests before code** — one at a time!
    - **Not refactoring** — the cycle is Red-Green-**Refactor**, not Red-Green-Red-Green
    - **Testing trivial code** — `def get_name(self): return self.name` doesn't need a test
    - **Mocking everything** — TDD works best with real objects and simple interfaces

---

## Practice Exercises

1. **TDD a `Queue` class** — follow the Red-Green-Refactor cycle strictly for: enqueue, dequeue, peek, size, is_empty.
2. **TDD a `BankAccount`** — start with deposit, then withdraw (with validation), then transfer between accounts.
3. **TDD a URL shortener** — shorten(), expand(), and stats tracking.
4. **TDD a roman numeral converter** — convert integers to Roman numerals one rule at a time.
5. **TDD a shopping cart** with add_item, remove_item, total, apply_discount.
