---
title: "Emerging Python Features"
description: New syntax and standard-library additions across recent Python versions
---

# Emerging Python Features <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🚀 Emerging & Evolving Python</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../core/beginner/python-basics/">Python Basics</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Structural pattern matching (`match`)
- [x] Modern union type syntax
- [x] Exception groups and `except*`
- [x] Built-in TOML reading
- [x] How to track what's coming next

The examples here are **verified on Python 3.13** (the version this site is built with). Each feature notes the version it arrived in.

---

## Structural pattern matching (3.10+)

The `match` statement brings powerful, readable branching — far beyond a simple switch. It can match values, guards, and *structure*. Runnable:

```python
def http_status(code):
    match code:
        case 200: return "OK"
        case 404: return "Not Found"
        case n if n >= 500: return "Server Error"    # guard condition
        case _: return "Unknown"                       # wildcard

print(http_status(200))    # OK
print(http_status(503))    # Server Error
print(http_status(302))    # Unknown
```

Output:

```text
OK
Server Error
Unknown
```

The real power is matching **structure** — destructuring tuples, lists, and objects in one step:

```python
def describe(point):
    match point:
        case (0, 0): return "origin"
        case (x, 0): return f"x-axis at {x}"
        case (0, y): return f"y-axis at {y}"
        case (x, y): return f"point {x},{y}"

print(describe((0, 0)))    # origin
print(describe((5, 0)))    # x-axis at 5
print(describe((3, 4)))    # point 3,4
```

Output:

```text
origin
x-axis at 5
point 3,4
```

Notice `case (x, 0)` both *matches* the shape (a 2-tuple ending in 0) and *binds* `x` — that combination of matching and destructuring is what makes it more than a switch.

---

## Modern union types (3.10+)

Write union types with `|` instead of `typing.Union`, and `X | None` instead of `Optional[X]`:

```python
def parse(x: int | str) -> str:      # was: Union[int, str]
    return str(x)

def find(key: str) -> dict | None:   # was: Optional[dict]
    ...
```

Cleaner and now the recommended style. See [Typing & Type Hints](../core/intermediate/typing.md).

---

## Exception groups & `except*` (3.11+)

When multiple things can fail at once (e.g. concurrent tasks), `ExceptionGroup` bundles several exceptions, and `except*` handles them by type. Runnable:

```python
try:
    raise ExceptionGroup("multiple failures", [
        ValueError("bad value"),
        TypeError("bad type"),
    ])
except* ValueError:
    print("handled a ValueError")
except* TypeError:
    print("handled a TypeError")
```

Output:

```text
handled a ValueError
handled a TypeError
```

Both handlers fire — `except*` processes *each* matching exception in the group, unlike normal `except` which stops at the first match. This matters for `asyncio.TaskGroup`, where several tasks may fail simultaneously.

---

## Built-in TOML reading (3.11+)

`tomllib` reads TOML (the format of `pyproject.toml`) with no third-party dependency:

```python
import tomllib

config = tomllib.loads('''
title = "demo"
[owner]
name = "Alice"
''')

print(config["title"])          # demo
print(config["owner"]["name"])  # Alice
```

Output:

```text
demo
Alice
```

Note: `tomllib` is **read-only** by design; to *write* TOML you still need a third-party library.

---

## Other notable recent additions

- **f-string improvements (3.12)** — f-strings became more flexible (nested quotes, multiline expressions).
- **`Self` type (3.11)** — annotate methods that return their own class cleanly.
- **Faster CPython (3.11+)** — significant speed gains, no code change needed (see [Runtime Evolution](runtime-evolution.md)).
- **Per-interpreter GIL / free-threading (3.12–3.13, experimental)** — the beginning of true parallelism (see [Runtime Evolution](runtime-evolution.md)).
- **Improved error messages (3.10+)** — Python now points at the exact spot and often suggests the fix.

---

## Staying current

- **What's New docs** — every release has an official "What's New in Python 3.x" page; the fastest way to see additions.
- **PEPs** — accepted proposals show what's landing next (Research → PEP Tracker).
- **Try the alpha/beta** — install a pre-release in a throwaway environment to experiment before it's stable.

!!! tip "Adopt with your minimum version in mind"
    A feature is only usable if every environment running your code supports it. `match` needs 3.10+, `tomllib` needs 3.11+. Check your project's `requires-python` before reaching for the newest syntax.

---

## Practice exercises

1. Rewrite an `if/elif` chain that dispatches on a value's *type* using `match` with class patterns.
2. Use `match` to destructure a dict with `case {"type": "user", "name": name}`.
3. Trigger an `ExceptionGroup` from two failing operations and handle each with `except*`.
4. Read your own `pyproject.toml` with `tomllib` and print the project name.
5. Read the "What's New" page for the latest Python release and list two additions you'd use.
