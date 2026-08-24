---
title: Garbage Collection
description: Reference counting, generational GC, cyclic references, weakref and the gc module
---

# Garbage Collection <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="memory-model/">Memory Model</a></span>
  </div>
</div>

---

## Two GC mechanisms in CPython

### 1. Reference Counting (primary)

Objects are freed **immediately** when their reference count drops to zero:

```python
import sys

class Tracked:
    def __del__(self):
        print(f"  __del__ called on {id(self)}")

obj = Tracked()
print(f"refcount: {sys.getrefcount(obj) - 1}")   # 1

del obj   # refcount → 0, immediately calls __del__
# Output: __del__ called on 140...
print("After del")
```

### 2. Cyclic Garbage Collector (supplementary)

Reference counting **cannot** handle reference cycles:

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.partner = None
    def __del__(self):
        print(f"  Collecting {self.name}")

a = Node("A")
b = Node("B")
a.partner = b     # A → B
b.partner = a     # B → A (cycle!)

# Both have refcount 2 (variable + partner reference)
del a   # refcount: 2 → 1 (still alive!)
del b   # refcount: 2 → 1 (still alive!)

# Neither is freed! They reference each other.
# The cyclic GC must detect and break the cycle.

import gc
gc.collect()
# Output:
#   Collecting A
#   Collecting B
```

---

## Generational Collection

The cyclic GC uses 3 **generations** based on the hypothesis that most objects die young:

| Generation | Contains | Collected |
|---|---|---|
| Gen 0 | Newly created objects | Most frequently |
| Gen 1 | Survived one collection | Less frequently |
| Gen 2 | Long-lived objects | Rarely |

```python
import gc

# View thresholds (objects_created, gen0→gen1, gen1→gen2)
print(gc.get_threshold())   # (700, 10, 10)
# Meaning: collect gen 0 after 700 new allocations
#           collect gen 1 after 10 gen-0 collections
#           collect gen 2 after 10 gen-1 collections

# View current counts
print(gc.get_count())   # (123, 4, 1) — objects in each gen

# View stats
print(gc.get_stats())
# [{'collections': 45, 'collected': 120, 'uncollectable': 0},
#  {'collections': 4,  'collected': 20,  'uncollectable': 0},
#  {'collections': 1,  'collected': 0,   'uncollectable': 0}]
```

---

## The `gc` module in detail

```python
import gc

# Force a full collection
collected = gc.collect()
print(f"Freed {collected} unreachable objects")

# Disable automatic collection (for latency-sensitive code)
gc.disable()
# ... latency-critical section ...
gc.enable()

# Find all objects that refer to a given object
x = [1, 2, 3]
y = {"data": x}
z = (x,)

referrers = gc.get_referrers(x)
print(len(referrers))   # includes y, z, and local frame

# Find all objects referred to BY a given object
refs = gc.get_referents(y)
print(refs)   # ['data', [1, 2, 3]]

# Check if GC is tracking an object
print(gc.is_tracked(x))   # True (container)
print(gc.is_tracked(42))  # False (int — no cycles possible)
```

---

## Which objects does the cyclic GC track?

The GC only tracks **container objects** that could potentially be part of cycles:

```python
import gc

# Tracked (containers)
print(gc.is_tracked([]))           # True
print(gc.is_tracked({}))           # True
print(gc.is_tracked(set()))        # True
print(gc.is_tracked(object()))     # True (has __dict__)

# NOT tracked (atomics — can't form cycles)
print(gc.is_tracked(42))           # False
print(gc.is_tracked("hello"))      # False
print(gc.is_tracked(3.14))         # False
print(gc.is_tracked(None))         # False
print(gc.is_tracked(True))         # False

# Tuples containing only atomics get UNTRACKED after creation
t = (1, 2, "three")
print(gc.is_tracked(t))            # False (optimization!)

t2 = (1, [2, 3])
print(gc.is_tracked(t2))           # True (contains mutable)
```

---

## `__del__` and its pitfalls

```python
import gc

class Resource:
    def __init__(self, name):
        self.name = name

    def __del__(self):
        print(f"  Closing {self.name}")
        # WARNING: during GC, other objects may already be collected!
        # Don't access other objects here if part of a cycle.

# Problem: __del__ objects in cycles were "uncollectable" in Python < 3.4
# Python 3.4+ (PEP 442): they CAN be collected, but in arbitrary order.
```

### Best practice: use context managers, not `__del__`

```python
# Bad
class BadFile:
    def __init__(self, path):
        self.f = open(path)
    def __del__(self):
        self.f.close()   # unreliable timing!

# Good
class GoodFile:
    def __init__(self, path):
        self.f = open(path)
    def close(self):
        self.f.close()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

with GoodFile("data.txt") as f:
    ...   # guaranteed close
```

---

## Breaking reference cycles

```python
import weakref

class Parent:
    def __init__(self):
        self.children = []

class Child:
    def __init__(self, parent):
        # Use weakref to avoid cycle
        self._parent_ref = weakref.ref(parent)

    @property
    def parent(self):
        return self._parent_ref()   # may return None

p = Parent()
c = Child(p)
p.children.append(c)

# No cycle! p → c (strong), c → p (weak)
del p   # p can be freed, c._parent_ref() returns None
```

---

## GC callbacks — monitoring collection

```python
import gc

def gc_callback(phase, info):
    if phase == "start":
        print(f"  GC starting gen {info['generation']}")
    elif phase == "stop":
        print(f"  GC done: collected {info['collected']}, "
              f"uncollectable {info['uncollectable']}")

gc.callbacks.append(gc_callback)

# Now every GC run triggers the callback
gc.collect()
# Output:
#   GC starting gen 2
#   GC done: collected 0, uncollectable 0
```

---

## Performance: tuning the GC

```python
import gc

# Increase threshold for fewer collections (trades memory for CPU)
gc.set_threshold(1400, 20, 20)   # default: (700, 10, 10)

# For real-time applications: manual control
gc.disable()

# Do latency-critical work...
# Periodically collect during idle moments
gc.collect(generation=0)   # fast — only gen 0
```

### Instagram's approach:
Instagram [disabled the GC entirely](https://instagram-engineering.com/dismissing-python-garbage-collection-at-instagram-4dca40b29172) after forking workers (to preserve copy-on-write memory sharing). They ensured no reference cycles existed in their code.

---

## `gc.freeze()` — optimize for fork-based servers (Python 3.7+)

```python
import gc

# Before forking worker processes:
gc.collect()    # collect all garbage
gc.freeze()     # move all objects to a permanent generation

# Now fork — the frozen objects won't be scanned by workers,
# preserving copy-on-write memory sharing
```

---

## Practice Exercises

1. **Create a reference cycle** between 3 objects, verify it leaks memory when GC is disabled, then enable GC and verify collection.
2. **Write a `gc_callback`** that logs all GC events to a file with timestamps.
3. **Measure the pause time** of `gc.collect()` on a large object graph (1M objects).
4. **Use `weakref`** to implement an observer pattern where observers don't prevent subject cleanup.
5. **Find all reference cycles** in a complex data structure using `gc.get_referrers` and `gc.get_referents`.
6. **Benchmark the performance impact** of disabling GC for a CPU-intensive task that creates no cycles.
