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

## try / except / else / finally

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

```python
try:
    data = process(raw_input)
except (ValueError, TypeError, KeyError) as e:
    print(f"Bad input: {e}")
```

---

## Raising exceptions

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Denominator cannot be zero")
    return a / b
```

---

## Custom exceptions

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

## Best practices

!!! tip "Error handling rules"
    - Catch specific exceptions, never bare `except:`
    - Use `else` for code that should only run on success
    - Use `finally` for cleanup (closing files, connections)
    - Raise early, catch late
    - Custom exceptions should inherit from `Exception`, not `BaseException`

---

## Practice exercises

1. Write a safe `get_integer()` function that keeps asking until the user enters a valid number.
2. Create a custom `ValidationError` with field name and message attributes.
3. Build a file processor that handles `FileNotFoundError`, `PermissionError` and `json.JSONDecodeError` gracefully.
