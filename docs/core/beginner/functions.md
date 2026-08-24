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

## Defining & Calling

```python
def greet(name):
    """Return a greeting string."""
    return f"Hello, {name}!"

print(greet("Alice"))   # Hello, Alice!
```

---

## Parameters

```python
# Positional
def add(a, b):
    return a + b

# Default values
def power(base, exp=2):
    return base ** exp

power(3)     # 9  (exp defaults to 2)
power(3, 3)  # 27

# Keyword arguments
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

describe(age=30, city="NYC", name="Alice")   # order doesn't matter

# *args — variable positional
def total(*numbers):
    return sum(numbers)

total(1, 2, 3, 4)   # 10

# **kwargs — variable keyword
def show(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

show(name="Alice", age=30)
```

---

## Return values

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

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()
```

Type hints don't enforce anything at runtime — they're for readability and tools like `mypy`.

---

## Practice exercises

1. Write a function `is_palindrome(s)` that returns `True` if the string reads the same forwards and backwards.
2. Write `fibonacci(n)` returning the nth Fibonacci number.
3. Write a closure `make_counter()` that returns a function — each call to that function returns the next integer starting from 1.
4. Write `apply_twice(f, x)` that applies function `f` to `x` twice.
