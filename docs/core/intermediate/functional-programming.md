---
title: Functional Programming
description: map, filter, reduce, functools, partial and functional patterns
---

# Functional Programming <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="iterators-generators/">Generators</a></span>
  </div>
</div>

---

## map, filter, reduce

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map — apply function to every element
squares = list(map(lambda x: x**2, numbers))

# filter — keep elements that pass the test
evens = list(filter(lambda x: x % 2 == 0, numbers))

# reduce — fold a sequence into a single value
total = reduce(lambda acc, x: acc + x, numbers, 0)
```

---

## functools.partial

`partial` pre-fills some of a function's arguments and returns a new callable that only needs
the rest. It's a clean way to specialize a general function without writing a wrapper.

```python
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)

print(square(5))   # 25
print(cube(3))     # 27
```

**When to use it:**

- **Callbacks** — bind arguments to a handler passed to a GUI/event system or `Timer`:
  `button.on_click(partial(save, document))`.
- **Predicates for `map`/`filter`/`sorted`** — e.g. `filter(partial(gt, threshold=10), nums)`.
- **Configuring library functions** — fix an encoding or base once:
  `read_utf8 = partial(open, encoding="utf-8")`.
- **Avoiding repetitive lambdas** — `partial(power, exp=2)` is clearer than `lambda b: power(b, 2)`.
- **Dependency injection** — pre-bind a logger, connection, or config so callers pass only the data.

---

## Higher-order function patterns

A **higher-order function** takes other functions as arguments or returns one. They let you
treat behavior as data — passing, combining, and building functions on the fly.

**When you'd use this:** composing a data-transformation pipeline from small steps, writing
`sorted`/`map`/`filter` keys, building decorators and middleware, implementing strategy/
callback patterns, and factoring out boilerplate into reusable wrappers.

```python
# Function composition
def compose(*fns):
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed

add_one  = lambda x: x + 1
double   = lambda x: x * 2
pipeline = compose(double, add_one)   # first add_one, then double
print(pipeline(3))   # 8
```

---

## Immutability patterns

```python
# Prefer tuple over list for fixed data
# Prefer frozenset over set for hashable collections
# Use dataclass(frozen=True) for immutable objects
# Avoid mutating arguments — return new values instead

def add_item(items: tuple, item) -> tuple:
    return items + (item,)   # returns new tuple, original unchanged
```

---

## Practice exercises

1. Implement `compose()` that chains N functions together.
2. Rewrite a loop-based data transformation using only `map`, `filter`, `reduce`.
3. Build a `pipeline()` function that takes data and a list of transformation functions.
