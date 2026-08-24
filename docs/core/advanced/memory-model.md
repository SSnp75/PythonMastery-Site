---
title: Memory Model
description: Object layout, id(), references, copying, __slots__ and memory internals
---

# Memory Model <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="cpython-internals/">CPython Internals</a></span>
  </div>
</div>

---

## Variables are references, not boxes

In Python, variables don't "contain" values — they're **name tags** pointing to objects:

```python
a = [1, 2, 3]
b = a            # b points to the SAME object

b.append(4)
print(a)         # [1, 2, 3, 4]  — both names see the change

print(id(a) == id(b))   # True — same memory address
print(a is b)            # True — identity check
```

### Assignment rebinds the name, it doesn't copy:

```python
a = [1, 2, 3]
b = a
b = [4, 5, 6]   # rebinds b to a NEW list
print(a)         # [1, 2, 3]  — a is unchanged
```

---

## `id()` — object identity

`id(obj)` returns the memory address of the object (in CPython):

```python
x = "hello"
print(id(x))       # e.g. 140234567890 (integer address)
print(hex(id(x)))  # 0x7f5a3b2c1234

# Same object → same id
y = x
print(id(x) == id(y))   # True

# Different object → different id (usually)
z = "hello"              # may be interned to same object
w = list(x)              # definitely new object
print(id(x) == id(w))   # False
```

!!! warning "id() is only unique while the object exists"
    After an object is garbage collected, its id can be reused by a new object.

---

## Mutable vs Immutable

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool` | `list` |
| `str`, `bytes` | `dict` |
| `tuple`, `frozenset` | `set` |
| `None` | Custom objects (usually) |

```python
# Immutable: operations create NEW objects
a = "hello"
b = a.upper()   # new string — a is untouched
print(id(a) == id(b))   # False

# Mutable: operations modify IN PLACE
c = [1, 2, 3]
d = c
c.append(4)     # mutates the same object
print(d)        # [1, 2, 3, 4]
```

---

## Shallow vs Deep Copy

```python
import copy

original = [[1, 2, 3], [4, 5, 6], {"key": "value"}]

# Shallow copy: new outer container, same inner objects
shallow = copy.copy(original)
# Also: list(original), original[:], original.copy()

shallow.append([7, 8, 9])   # doesn't affect original
print(len(original))        # 3 (unaffected)

shallow[0].append(99)       # DOES affect original!
print(original[0])          # [1, 2, 3, 99]  ← shared inner list

# Deep copy: recursively copies everything
deep = copy.deepcopy(original)
deep[0].append(888)
print(original[0])          # [1, 2, 3, 99]  ← unaffected
```

### When to use which:

| Scenario | Method |
|---|---|
| Top-level container only | `copy.copy()` or `list()` |
| Nested mutable objects | `copy.deepcopy()` |
| Immutable contents | No copy needed (share safely) |
| Performance-critical | Avoid deep copy, design with immutables |

---

## Object sizes and `sys.getsizeof`

```python
import sys

# Basic objects
print(sys.getsizeof(None))         # 16
print(sys.getsizeof(True))         # 28
print(sys.getsizeof(0))            # 28
print(sys.getsizeof(2**30))        # 32
print(sys.getsizeof(2**60))        # 36

# Containers (shallow — doesn't count contents)
print(sys.getsizeof([]))           # 56
print(sys.getsizeof([1]))          # 64
print(sys.getsizeof([1,2,3,4,5]))  # 96

print(sys.getsizeof({}))           # 64
print(sys.getsizeof({"a": 1}))     # 184

print(sys.getsizeof(""))           # 49
print(sys.getsizeof("a"))          # 50
print(sys.getsizeof("hello"))      # 54
```

### True deep size:

```python
def deep_getsizeof(obj, seen=None):
    """Recursively compute total memory of an object graph."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen)
                    for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(i, seen) for i in obj)
    elif hasattr(obj, '__dict__'):
        size += deep_getsizeof(obj.__dict__, seen)

    return size

data = {"users": [{"name": "Alice", "scores": [95, 87, 92]}] * 100}
print(f"Shallow: {sys.getsizeof(data)} bytes")
print(f"Deep: {deep_getsizeof(data)} bytes")
```

---

## tracemalloc — tracking memory allocations

```python
import tracemalloc

tracemalloc.start()

# Code to measure
data = [list(range(1000)) for _ in range(1000)]

snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics("lineno")

print("Top 5 memory consumers:")
for stat in stats[:5]:
    print(f"  {stat}")
```

Output:
```
Top 5 memory consumers:
  script.py:6: size=8017 KiB, count=1001, average=8201 B
```

---

## Memory-efficient patterns

### Use `__slots__` for data-heavy classes:

```python
class PointSlots:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class PointDict:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# Create 1 million points
import sys
slots_list = [PointSlots(i, i, i) for i in range(100_000)]
dict_list  = [PointDict(i, i, i) for i in range(100_000)]

print(f"Slots: {sys.getsizeof(slots_list[0])} bytes each")  # ~56
print(f"Dict:  {sys.getsizeof(dict_list[0]) + sys.getsizeof(dict_list[0].__dict__)} bytes each")  # ~168
```

### Use generators instead of lists for streaming:

```python
# Bad — stores all in memory
all_lines = [line.strip() for line in open("huge.txt")]

# Good — streams one line at a time
def stripped_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()
```

### Use `array.array` for homogeneous numeric data:

```python
import array, sys

py_list = list(range(1_000_000))
c_array = array.array('i', range(1_000_000))

print(f"List:  {sys.getsizeof(py_list):>10,} bytes")   # ~8.4 MB
print(f"Array: {sys.getsizeof(c_array):>10,} bytes")   # ~4.0 MB
# NumPy array would be even smaller + faster
```

---

## Weak References

Normal references keep objects alive. Weak references allow the object to be garbage collected:

```python
import weakref

class ExpensiveObject:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print(f"  {self.name} deleted")

obj = ExpensiveObject("resource")
weak = weakref.ref(obj)

print(weak())          # <ExpensiveObject object>
print(weak().name)     # resource

del obj                # Output: resource deleted
print(weak())          # None — object was collected
```

### WeakValueDictionary — cache that doesn't prevent GC:

```python
cache = weakref.WeakValueDictionary()

def get_data(key):
    if key in cache:
        return cache[key]
    data = ExpensiveObject(key)   # expensive creation
    cache[key] = data
    return data
```

---

## Practice Exercises

1. **Create a reference cycle** and show that `del` doesn't free the memory (need `gc.collect()`).
2. **Implement `deep_getsizeof`** and measure the true memory of a nested data structure.
3. **Compare memory usage** of 1M objects with `__slots__` vs without.
4. **Use `tracemalloc`** to find the top 3 memory allocations in a complex script.
5. **Build a weak-reference cache** that expires entries when no strong references exist.
6. **Demonstrate that tuple reuse** happens for small tuples: `() is ()` is True.
