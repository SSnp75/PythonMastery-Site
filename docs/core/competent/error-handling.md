---
title: Error Handling
description: Exceptions, try/except, raising errors and custom exceptions
---

# Error Handling <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

---

!!! info "When you'd use this"
    Exceptions, try/except, raising errors and custom exceptions.

    Make code robust: catch specific failures, add context with exception chaining, define a custom exception hierarchy, and clean up with `finally`.


## try / except / else / finally

*The core structure: `try` the risky code, `except` specific failures, `else` for the success path, `finally` for cleanup that always runs. Use it anywhere an operation can fail.*

```python
try:
    result = int(input("Enter a number: "))
    print(10 / result)
except ValueError:
    print("Not a valid number!")
except ZeroDivisionError:
    print("Cannot divide by zero!")
else:
    print("Success — no errors")   # runs only if no exception
finally:
    print("Always runs")            # cleanup code
```

---

## Catching multiple exceptions

*Group related failures in one `except (A, B)` when they share handling, or use separate clauses when each needs a different response.*

```python
try:
    data = process(raw_input)
except (ValueError, TypeError, KeyError) as e:
    print(f"Bad input: {e}")
```

---

## Raising exceptions

*Signal a problem yourself with `raise` — validate inputs and fail loudly with a clear message instead of returning a bad value.*

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Denominator cannot be zero")
    return a / b
```

---

## Custom exceptions

*Define your own exception types to carry domain context and let callers catch exactly what they care about. Inherit from `Exception`, not `BaseException`.*

```python
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount  = amount
        super().__init__(
            f"Cannot withdraw ${amount}: only ${balance} available"
        )

class BankAccount:
    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount
```

---

## Exception chaining (`raise ... from`)

Preserve the original cause when re-raising as a higher-level error:

```python
class ConfigError(Exception):
    pass

def load_port(raw):
    try:
        return int(raw)
    except ValueError as e:
        raise ConfigError("port must be an integer") from e

try:
    load_port("abc")
except ConfigError as e:
    print(type(e).__name__, "->", type(e.__cause__).__name__)
    # ConfigError -> ValueError
```

---

## A custom exception hierarchy

Give an app one base exception so callers can catch broadly or narrowly:

```python
class AppError(Exception): ...
class NotFoundError(AppError): ...
class PermissionError_(AppError): ...

def handle(e):
    return isinstance(e, AppError)

print(handle(NotFoundError()))   # True — one base catches all app errors
```

---

## Exception groups (Python 3.11+)

Handle multiple simultaneous errors (e.g. from concurrent tasks) with `except*`:

```python
import sys

if sys.version_info >= (3, 11):
    try:
        raise ExceptionGroup("many", [ValueError("v"), TypeError("t")])
    except* ValueError as eg:
        print("caught ValueErrors:", len(eg.exceptions))   # 1
    except* TypeError as eg:
        print("caught TypeErrors:", len(eg.exceptions))     # 1
```

---

## `contextlib.suppress` — ignore an expected error

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    open("does-not-exist.txt")
print("continued without crashing")   # continued without crashing
```

---

## EAFP vs LBYL

Python prefers **EAFP** (Easier to Ask Forgiveness than Permission) — try the operation and
handle failure — over **LBYL** (Look Before You Leap):

```python
d = {"a": 1}

# EAFP (Pythonic)
try:
    v = d["b"]
except KeyError:
    v = 0
print(v)   # 0

# LBYL (more code, races in concurrent settings)
v = d["b"] if "b" in d else 0
print(v)   # 0
```

---

## Best practices

!!! tip "Error handling rules"
    - Catch specific exceptions, never bare `except:`
    - Use `else` for code that should only run on success
    - Use `finally` for cleanup (closing files, connections)
    - Chain with `raise ... from` to preserve the original cause
    - Raise early, catch late
    - Custom exceptions should inherit from `Exception`, not `BaseException`

---

## Practice exercises

1. Write a safe `get_integer()` function that keeps asking until the user enters a valid number.
2. Create a custom `ValidationError` with field name and message attributes.
3. Build a file processor that handles `FileNotFoundError`, `PermissionError` and `json.JSONDecodeError` gracefully.
