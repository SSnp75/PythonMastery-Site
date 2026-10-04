---
title: Functions
description: Defining functions, parameters, scope, closures and lambda
---

# Functions <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="control-flow/">Control Flow</a></span>
  </div>
</div>

<div class="pm-next">
<strong>✅ What's next</strong>
<a href="../intermediate/decorators/">Decorators</a>
<a href="../intermediate/functional-programming/">Functional Programming</a>
</div>

---

!!! info "When you'd use this"
    Defining functions, parameters, scope, closures and lambda.

    Factor repeated logic into named, reusable units — anytime you copy-paste code, a function (with parameters, defaults, or *args) is the fix.


## Defining & Calling

*Package reusable logic behind a name with `def`, then run it by calling `name(args)`. Use it the moment you'd otherwise repeat the same lines.*

```python
def greet(name):
    """Return a greeting string."""
    return f"Hello, {name}!"

print(greet("Alice"))   # Hello, Alice!
```

---

## Parameters

*Control how callers pass data: positional, defaults, keyword, and variable `*args`/`**kwargs`. Use defaults for optional settings and `*args`/`**kwargs` for flexible, wrapper-style APIs.*

```python
# Positional
def add(a, b):
    return a + b

# Default values
def power(base, exp=2):
    return base ** exp

print(power(3))      # 9   (exp defaults to 2)
print(power(3, 3))   # 27

# Keyword arguments
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

print(describe(age=30, city="NYC", name="Alice"))   # Alice, 30, from NYC

# *args — variable positional
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3, 4))   # 10

# **kwargs — variable keyword
def show(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

show(name="Alice", age=30)
# name: Alice
# age: 30
```

---

## Return values

*Send a result back with `return`; return a tuple to hand back several values at once. Use it whenever a caller needs the computed answer rather than a side effect.*

```python
# Return multiple values (actually a tuple)
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(lo, hi)   # 1 9

# Returning None explicitly
def log(msg):
    print(msg)
    # implicit return None
```

---

## Scope (LEGB Rule)

*Where a name is looked up: Local → Enclosing → Global → Built-in. Understanding it explains "why is this variable `None`/undefined?" bugs and when you need `global`/`nonlocal`.*

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)   # local

    inner()
    print(x)       # enclosing

outer()
print(x)           # global
```

| Scope | Where |
|---|---|
| **L**ocal | Inside current function |
| **E**nclosing | In the surrounding function (closures) |
| **G**lobal | Module level |
| **B**uilt-in | Python built-ins (`len`, `print`, etc.) |

---

## Closures

*An inner function that remembers variables from the scope it was created in. Use it for function factories, callbacks that carry state, and as the mechanism behind decorators.*

```python
def make_multiplier(n):
    def multiply(x):
        return x * n    # n is captured from enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
```

Closures are the foundation of decorators. Study them well.

---

## Lambda Functions

*Tiny one-expression anonymous functions. Use them inline as a `key=` for `sorted`/`min`/`max` or a quick callback — not as a replacement for a named `def`.*

```python
# Single-expression anonymous functions
square = lambda x: x ** 2
print(square(5))   # 25

# Useful with sorted, map, filter
names = ["Charlie", "Alice", "Bob"]
sorted_names = sorted(names, key=lambda n: len(n))
print(sorted_names)   # ['Bob', 'Alice', 'Charlie']
```

!!! tip "When to use lambda"
    Only for simple, short expressions passed directly to another function. For anything with more than one expression, use a regular `def`.

---

## Type Hints on Functions

*Annotate parameter and return types for readability and tooling. Use them on anything shared or non-trivial so `mypy` and your editor can catch mistakes early.*

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()

print(greet("Alice", 2))   # Hello, Alice! Hello, Alice!
```

Type hints don't enforce anything at runtime — they're for readability and tools like `mypy`.

---

## Practice exercises

1. Write a function `is_palindrome(s)` that returns `True` if the string reads the same forwards and backwards.
2. Write `fibonacci(n)` returning the nth Fibonacci number.
3. Write a closure `make_counter()` that returns a function — each call to that function returns the next integer starting from 1.
4. Write `apply_twice(f, x)` that applies function `f` to `x` twice.
