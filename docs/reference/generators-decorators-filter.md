---
title: "Generators, Decorators & Filtering — Deep Dive"
description: Practical patterns for generators (yield from, pipelines, streaming), decorators (factories, class-based), and filter/map/reduce
---

# Generators, Decorators & Filtering <span class="pm-badge pm-badge-intermediate">Deep Dive</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../core/intermediate/iterators-generators/">Generators</a></span>
  </div>
</div>

<div class="pm-next">
<strong>✅ Related</strong>
<a href="../core/intermediate/decorators/">Decorators</a>
<a href="../core/intermediate/functional-programming/">Functional Programming</a>
<a href="cheatsheets.md">Cheat Sheets</a>
</div>

---

A pattern catalog for three closely related tools: **generators** (lazy, streaming data),
**decorators** (wrapping behavior), and **filtering** (`filter`/`map`/`reduce`). Every example
below runs as-is.

---

## Generators

### Infinite generators

A generator with `while True` produces values forever — safe because they're lazy. Pull with `next()`.

```python
def infinite_counter():
    n = 1
    while True:
        yield n
        n += 1

counter = infinite_counter()
print(next(counter))   # 1
print(next(counter))   # 2
```

---

### `yield from` — delegation

`yield from X` delegates to another generator or iterable. It is shorthand for:

```python
for item in X:
    yield item
```

What `yield from` does for you:

- Runs the inner loop automatically
- Passes values both ways (`send`, `throw`)
- Propagates the sub-generator's **return value**
- Keeps nested generators clean and readable

```python
def numbers():
    yield from range(3)

def letters():
    yield from ["A", "B", "C"]

def combined():
    yield from numbers()
    yield from letters()

print(list(combined()))   # [0, 1, 2, 'A', 'B', 'C']
```

---

### `yield from` returns a value from a sub-generator

A `return` inside a generator becomes the value of the `yield from` expression (not part of the stream).

```python
def child():
    yield 1
    yield 2
    return "done!"

def parent():
    result = yield from child()
    print("Child returned:", result)

for x in parent():
    print(x)

# 1
# 2
# Child returned: done!
```

---

### Generators in data pipelines

Chain generators like Unix pipes. Nothing is computed until you iterate — memory stays flat even for huge inputs.

```python
def numbers():
    for i in range(1_000_000):
        yield i

def evens(nums):
    for n in nums:
        if n % 2 == 0:
            yield n

def squared(nums):
    for n in nums:
        yield n * n

pipeline = squared(evens(numbers()))

print(next(pipeline))   # 0
print(next(pipeline))   # 4
print(next(pipeline))   # 16
```

!!! tip "Why pipelines matter"
    Each stage pulls one item at a time from the stage before it. A million-item source
    never materializes as a list — this is the same pattern used in log processing,
    streaming APIs, and real-time data pipelines.

---

### Streaming: files, logs, sockets

```python
# Stream CSV rows without loading the whole file
def read_csv(filename):
    with open(filename) as f:
        for row in f:
            yield row.rstrip("\n").split(",")

# Tail a log file (like `tail -f`)
def follow(file):
    file.seek(0, 2)              # jump to end of file
    while True:
        line = file.readline()
        if not line:
            continue             # no new line yet — keep waiting
        yield line

# Stream chunks from a socket until it closes
def stream_socket(sock):
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        yield chunk
```

---

## Decorators

A decorator is a function that **takes a function, adds behavior, and returns a new function** —
without modifying the original. Common uses: logging, timing, authentication, caching,
validation, retry logic, resource management.

### Mental model

```python
@decorator
def f():
    pass

# is exactly equivalent to:
f = decorator(f)
```

> function → wrapped with extra behavior → new function

```python
def decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@decorator
def greet():
    print("Hello")

greet()
# Before
# Hello
# After
```

---

### Practical example: logging

```python
from functools import wraps

def log(func):
    @wraps(func)                 # preserve name & docstring
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def add(a, b):
    return a + b

print(add(3, 4))
# Calling add
# 7
```

---

### Decorators with arguments

A decorator that takes arguments is a function returning a decorator (three nested levels).

```python
from functools import wraps

def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def hello():
    print("Hello")

hello()
# Hello
# Hello
# Hello
```

---

### Decorators + generators

A decorator can adapt a generator's output — e.g. materialize it into a list.

```python
def to_list(func):
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))
    return wrapper

@to_list
def numbers():
    yield 1
    yield 2
    yield 3

print(numbers())   # [1, 2, 3]
```

---

### Class-based decorators

Use a class with `__call__` when the decorator needs to hold state across calls.

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print("Call number:", self.count)
        return self.func(*args, **kwargs)

@CountCalls
def greet():
    print("Hi")

greet()
greet()
# Call number: 1
# Hi
# Call number: 2
# Hi
```

---

## Filtering with `filter`, `map`, `reduce`

### The three building blocks

```python
from functools import reduce

a = [1, 2, 3, 4, 5]

# map — transform every element
print(list(map(lambda x: x ** 2, a)))        # [1, 4, 9, 16, 25]

# filter — keep elements where the predicate is True
print(list(filter(lambda x: x % 2 == 0, a))) # [2, 4]

# reduce — fold into a single value
print(reduce(lambda x, y: x * y, a))         # 120  (1*2*3*4*5)
```

!!! warning "A common filter bug"
    `filter(lambda x: x * 2, a)` does **not** keep even numbers — `x * 2` is truthy for
    almost every number, so nothing is filtered. To keep evens, test a boolean:
    `filter(lambda x: x % 2 == 0, a)`.

---

### Pattern catalog

#### Drop falsy values

When the function is `None`, `filter` removes falsy items (`""`, `0`, `None`, `False`).

```python
items = ["", "hello", 0, 42, None, "world", False]
clean = list(filter(None, items))
print(clean)   # ['hello', 42, 'world']
```

#### Filter by type

```python
data = [1, "a", 2.5, 3, "b"]
ints = list(filter(lambda x: isinstance(x, int), data))
print(ints)   # [1, 3]
```

#### Filter objects by attribute

```python
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob",   "age": 35},
    {"name": "Cara",  "age": 40},
]
older = list(filter(lambda u: u["age"] > 30, users))
print([u["name"] for u in older])   # ['Bob', 'Cara']
```

#### Multiple conditions

```python
nums = range(1, 20)
result = list(filter(lambda x: x % 2 == 0 and x % 3 == 0, nums))
print(result)   # [6, 12, 18]
```

#### Dynamic threshold (external state via closure)

```python
threshold = 50
values = [10, 60, 30, 80, 55]
filtered = list(filter(lambda x: x > threshold, values))
print(filtered)   # [60, 80, 55]
```

#### Named function for complex logic

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = list(filter(is_prime, range(1, 20)))
print(primes)   # [2, 3, 5, 7, 11, 13, 17, 19]
```

#### Filter a dictionary

```python
data = {"a": 5, "b": 15, "c": 8, "d": 20}
filtered = dict(filter(lambda kv: kv[1] > 10, data.items()))
print(filtered)   # {'b': 15, 'd': 20}
```

#### Filter nested structures

```python
users = [
    {"name": "Alice", "roles": ["user"]},
    {"name": "Bob",   "roles": ["admin", "user"]},
    {"name": "Cara",  "roles": []},
]
admins = list(filter(lambda u: "admin" in u["roles"], users))
print([u["name"] for u in admins])   # ['Bob']
```

#### Filter an infinite generator (lazy pipeline)

```python
from itertools import islice

def numbers():
    n = 1
    while True:
        yield n
        n += 1

evens = filter(lambda x: x % 2 == 0, numbers())
print(list(islice(evens, 5)))   # [2, 4, 6, 8, 10]
```

Generator → filter → `islice`: an infinite source, a lazy predicate, and controlled
consumption. Nothing runs until `list()` pulls the first five.

#### Filter log lines

```python
lines = [
    "INFO: system running",
    "ERROR: disk failure",
    "WARNING: low memory",
    "ERROR: overheating",
]
errors = list(filter(lambda line: "ERROR" in line, lines))
print(errors)   # ['ERROR: disk failure', 'ERROR: overheating']
```

#### Validation & regex

```python
import re

emails = ["a@b.com", "invalid", "x@y.org", "nope"]
valid = list(filter(lambda e: "@" in e and "." in e, emails))
print(valid)   # ['a@b.com', 'x@y.org']

words = ["cat", "dog", "car", "cart", "apple"]
pattern = re.compile(r"^ca")
print(list(filter(lambda w: pattern.match(w), words)))   # ['cat', 'car', 'cart']
```

#### Data cleaning (drop blank/whitespace strings)

```python
data = ["hello", "   ", "world", "", "  ai  "]
clean = list(filter(lambda s: s.strip(), data))
print(clean)   # ['hello', 'world', '  ai  ']
```

#### Parameterized predicate with `functools.partial`

```python
from functools import partial

def greater(x, threshold):
    return x > threshold

gt10 = partial(greater, threshold=10)   # pre-fill threshold
print(list(filter(gt10, [5, 10, 15, 20])))   # [15, 20]
```

#### Filter → map → reduce pipeline

```python
from functools import reduce

nums = [1, 2, 3, 4, 5, 6]
pipeline = reduce(
    lambda acc, x: acc + [x * 10],
    filter(lambda x: x % 2 == 0, nums),
    [],
)
print(pipeline)   # [20, 40, 60]
```

---

### Deduplication — clever, but prefer the explicit version

You may see this one-liner that keeps first occurrences:

```python
seen = set()
nums = [1, 2, 2, 3, 1, 4]
unique = list(filter(lambda x: not (x in seen or seen.add(x)), nums))
print(unique)   # [1, 2, 3, 4]
```

It works because `x in seen` short-circuits, and `seen.add(x)` returns `None` (falsy) while
mutating the set. But a side effect inside a lambda is hard to read. Prefer this:

```python
def dedupe(items):
    seen = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            yield x

print(list(dedupe([1, 2, 2, 3, 1, 4])))   # [1, 2, 3, 4]
```

Or simply `list(dict.fromkeys(nums))`, which preserves order since Python 3.7.

---

## Practice exercises

1. Write a generator `batched(iterable, n)` that yields lists of up to `n` items. Compare with `itertools.batched` (3.12+).
2. Build a three-stage generator pipeline that reads lines, strips whitespace, and keeps only non-empty ones.
3. Write a `@retry(times=3)` decorator factory that re-runs a function on exception.
4. Write a class-based `@Timer` decorator that accumulates total time spent in a function across all calls.
5. Rewrite a nested `for`/`if` loop that collects results into a single `filter` + `map` expression.
6. Implement `unique_by(key)` that filters an iterable to the first item per key value.
