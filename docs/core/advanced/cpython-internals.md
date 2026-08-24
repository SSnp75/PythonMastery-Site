---
title: CPython Internals
description: Object model, reference counting, GIL, type slots and the C implementation
---

# CPython Internals <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisite: <a href="bytecode/">Bytecode</a></span>
  </div>
</div>

---

## Everything is a PyObject

In the C source, every Python object starts with a common header:

```c
// Simplified from Include/object.h
typedef struct {
    Py_ssize_t ob_refcnt;    // reference count
    PyTypeObject *ob_type;   // pointer to type object
} PyObject;
```

This means:
- `sys.getrefcount(obj)` reads `ob_refcnt`
- `type(obj)` reads `ob_type`

```python
import sys

x = []
print(sys.getrefcount(x))   # 2 (x + the getrefcount arg)

y = x
print(sys.getrefcount(x))   # 3 (x + y + the getrefcount arg)

del y
print(sys.getrefcount(x))   # 2
```

---

## Reference Counting

CPython's primary memory management is **reference counting** — each object tracks how many references point to it:

```python
import sys

a = "hello"             # refcount = 1
b = a                   # refcount = 2 (a and b)
c = [a, a, a]           # refcount = 5 (a, b, c[0], c[1], c[2])
print(sys.getrefcount(a))  # 6 (includes getrefcount's own ref)

del b                   # refcount decreases
c.clear()              # refcount decreases by 3
```

When refcount hits 0, the object is **immediately** deallocated — no waiting for a GC cycle.

### Advantages:
- Deterministic destruction (predictable `__del__` timing)
- Low latency (no GC pauses for simple cases)
- Simple mental model

### Disadvantages:
- Can't handle reference cycles (need supplementary GC)
- Thread-unsafe without the GIL
- Per-object overhead (8 bytes for refcount on 64-bit)

---

## The GIL (Global Interpreter Lock)

The GIL is a mutex that allows only **one thread** to execute Python bytecode at a time.

```python
import threading, time

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1   # NOT atomic — but GIL prevents corruption

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()

# counter might be less than 2_000_000!
# GIL prevents memory corruption but NOT race conditions
# because += is multiple bytecodes: LOAD, ADD, STORE
```

### When the GIL is released:
- During I/O operations (file read, network, sleep)
- During C extension calls that explicitly release it
- Every N bytecodes (sys.getswitchinterval(), default 5ms)

### Implications:
- Multi-threaded CPU-bound code won't use multiple cores
- I/O-bound code benefits from threads (GIL released during I/O)
- `multiprocessing` bypasses the GIL entirely (separate processes)

### The future: free-threading (PEP 703)
Python 3.13+ has experimental support for running without the GIL:
```bash
python3.13t script.py   # free-threaded build
```

---

## Small Integer Cache

CPython caches integers from **-5 to 256**:

```python
a = 256
b = 256
print(a is b)   # True — same object

a = 257
b = 257
print(a is b)   # False — different objects (usually)

a = -5
b = -5
print(a is b)   # True

a = -6
b = -6
print(a is b)   # False
```

This exists purely as an optimization — small integers are used so frequently that caching avoids millions of allocations.

---

## String Interning

CPython interns certain strings (stores only one copy):

```python
a = "hello"
b = "hello"
print(a is b)   # True — interned (looks like an identifier)

a = "hello world"
b = "hello world"
print(a is b)   # False — contains space, not interned automatically

import sys
a = sys.intern("hello world")
b = sys.intern("hello world")
print(a is b)   # True — manually interned
```

Interning rules:
- Strings that look like identifiers (`[a-zA-Z_][a-zA-Z0-9_]*`) are auto-interned
- Dictionary keys are interned
- Module attribute names are interned
- You can force-intern with `sys.intern()`

---

## Object Allocation: pymalloc

CPython has its own memory allocator for small objects (< 512 bytes):

```
┌─────────────────────────────────┐
│ OS (malloc/mmap)                │  ← large allocations
├─────────────────────────────────┤
│ Python Object Allocator         │  ← arenas (256 KB)
│   └── Pools (4 KB each)        │     └── blocks (8, 16, 24...512 bytes)
├─────────────────────────────────┤
│ Python Internal Buffer          │  ← raw memory API
└─────────────────────────────────┘
```

```python
import sys

# Every object has overhead
print(sys.getsizeof(0))        # 28 bytes (on 64-bit)
print(sys.getsizeof(1))        # 28 bytes
print(sys.getsizeof(2**30))    # 32 bytes
print(sys.getsizeof(""))       # 49 bytes
print(sys.getsizeof("a"))      # 50 bytes
print(sys.getsizeof([]))       # 56 bytes
print(sys.getsizeof({}))       # 64 bytes
```

---

## Type Slots — How methods are dispatched

When you write `a + b`, CPython doesn't look up `__add__` in a dictionary. Instead, it checks a **type slot**:

```c
// Simplified: how + works internally
PyObject* binary_add(PyObject *a, PyObject *b) {
    // Check the type's nb_add slot (C function pointer)
    binaryfunc add_func = a->ob_type->tp_as_number->nb_add;
    if (add_func) {
        return add_func(a, b);
    }
    // ... try reflected (b.__radd__), then TypeError
}
```

This is why built-in types are faster than pure Python classes — their operations are C function pointers, not dictionary lookups.

```python
import timeit

# Built-in int addition (C slot)
print(timeit.timeit("1 + 2", number=10_000_000))   # ~0.3s

# Custom class addition (dict lookup → Python call)
class MyInt:
    def __init__(self, v): self.v = v
    def __add__(self, other): return MyInt(self.v + other.v)

a, b = MyInt(1), MyInt(2)
print(timeit.timeit("a + b", globals={"a": a, "b": b}, number=10_000_000))  # ~3s
```

---

## `__slots__` vs `__dict__`

```python
import sys

class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WithSlots:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

d = WithDict(1, 2)
s = WithSlots(1, 2)

print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))   # ~168 bytes
print(sys.getsizeof(s))                                 # ~56 bytes

# Slots are 3x more memory efficient for data-heavy classes
# Also slightly faster attribute access (array lookup vs dict lookup)
```

---

## Examining CPython source patterns

The CPython source is at `github.com/python/cpython`. Key directories:

| Path | Content |
|---|---|
| `Python/ceval.c` | The bytecode evaluation loop |
| `Objects/longobject.c` | Integer implementation |
| `Objects/listobject.c` | List implementation |
| `Objects/dictobject.c` | Dictionary implementation |
| `Include/object.h` | PyObject struct definition |
| `Modules/` | Built-in C modules (math, json, etc.) |

---

## Practice Exercises

1. **Demonstrate reference counting** — create a chain of references, delete them one by one, observe `sys.getrefcount` changes.
2. **Find the boundaries** of the small integer cache by testing `is` identity from -10 to 300.
3. **Measure the memory difference** between a class with `__slots__` vs without for 1 million instances.
4. **Show that the GIL prevents multi-threaded CPU speedup** by timing a CPU-bound function with 1 thread vs 4 threads.
5. **Compare attribute access speed** for a regular class, a `__slots__` class, and a `namedtuple`.
6. **Read the CPython source for `list.append`** at `Objects/listobject.c` and explain the over-allocation strategy.
