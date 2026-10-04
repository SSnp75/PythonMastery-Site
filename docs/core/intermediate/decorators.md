---
title: Decorators
description: Closures, functools.wraps, class decorators and decorator patterns
---

# Decorators <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../beginner/functions/">Functions (Closures)</a></span>
  </div>
</div>

---

!!! info "When you'd use this"
    Closures, functools.wraps, class decorators and decorator patterns.

    Wrap behavior around functions without touching their code — logging, timing, caching, authentication, retries, and rate limiting.


## What is a decorator?

A function that takes a function and returns a modified function.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Alice")
# Before
# Hello, Alice!
# After
```

---

## functools.wraps — always use it

*Copies the wrapped function's name, docstring, and metadata onto the wrapper. Always apply it, or tools, tracebacks, and `help()` will show "wrapper" instead of the real function.*

```python
from functools import wraps

def timer(func):
    @wraps(func)   # preserves original name & docstring
    def wrapper(*args, **kwargs):
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    """This is a slow function."""
    import time
    time.sleep(1)

print(slow_function.__name__)   # "slow_function" (not "wrapper")
```

---

## Decorators with arguments

*A decorator that takes config needs an extra layer: a function returning a decorator. Use it for `@retry(times=3)`, `@route("/path")`, `@cache(ttl=60)`-style parameterized behavior.*

```python
def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")   # prints 3 times
```

---

## Class-based decorators

*Use a class with `__call__` when the decorator must hold state across calls (counts, caches, registries) — cleaner than nested closures with `nonlocal`.*

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()   # Call #1 \n Hi!
say_hi()   # Call #2 \n Hi!
print(say_hi.count)   # 2
```

---

## Stacking decorators

*Apply several decorators to one function — they wrap bottom-up. Order matters: `@timer` over `@repeat(3)` times all three runs together.*

```python
@timer
@repeat(3)
def process():
    pass

# Equivalent to: timer(repeat(3)(process))
# Order matters — bottom decorator applies first
```

---

## Real-world patterns

*The payoff: cross-cutting concerns like retry, caching, auth, and rate limiting applied declaratively with one line, instead of cluttering every function body.*

```python
# Retry decorator
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=5, delay=2)
def unreliable_api_call():
    ...
```

---

## Practice exercises

1. Write a `@cache` decorator that memoizes function results.
2. Write a `@validate_types` decorator that checks argument types at runtime.
3. Write a `@log_calls` decorator that logs function name, args and return value.
4. Write a `@singleton` class decorator that ensures only one instance exists.
