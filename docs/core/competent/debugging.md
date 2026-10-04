---
title: Debugging
description: pdb, breakpoints, print debugging and logging
---

# Debugging <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="error-handling/">Error Handling</a></span>
  </div>
</div>

---

## The built-in debugger (pdb)

*Pause execution and inspect/step through live state with `breakpoint()`. Reach for it when print-debugging isn't enough — complex control flow or state you need to poke at.*

```python
# Add breakpoint in your code
def buggy_function(data):
    breakpoint()                  # Python 3.7+ — drops into pdb
    result = process(data)
    return result
```

### Key pdb commands

| Command | Action |
|---|---|
| `n` | Next line (step over) |
| `s` | Step into function call |
| `c` | Continue to next breakpoint |
| `p expr` | Print expression |
| `l` | List source code around current line |
| `w` | Show call stack |
| `q` | Quit debugger |

---

## Logging (better than print)

*Record diagnostics with levels you can filter — the right tool for anything beyond a throwaway script, and essential in production where you can't watch stdout.*

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

logger.debug("Variable x = %s", 42)
logger.info("Processing started")
logger.warning("Disk space low")
logger.error("Failed to connect")
logger.critical("System crash!")
```

Use `%s` placeholders (not f-strings) so the string is only formatted if the level is active.

---

## Post-mortem: inspect a crash after it happens

*Post-mortem: inspect a crash after it happens in Debugging — what it is and when to use it.*

```python
import pdb

def boom():
    x = 10
    return x / 0

try:
    boom()
except ZeroDivisionError:
    # pdb.post_mortem()  # drops into the frame where it crashed
    pass
```

`pdb.post_mortem()` opens the debugger at the exact frame that raised — you can inspect
locals (`x` here) without re-running.

---

## Reading tracebacks programmatically

*Reading tracebacks programmatically in Debugging — what it is and when to use it.*

```python
import traceback

try:
    [][5]
except IndexError:
    tb = traceback.format_exc()
    print("IndexError" in tb)   # True
```

`traceback.format_exc()` returns the full traceback as a string — handy for logging.

---

## Quick inspection helpers

*Quick inspection helpers in Debugging — what it is and when to use it.*

```python
# What attributes/methods does an object have?
print([m for m in dir("x") if not m.startswith("_")][:3])   # ['capitalize', 'casefold', 'center']

# Where is this object in memory / what type?
print(type(42).__name__)   # int

# Introspect a function's signature
import inspect
def f(a, b=2): ...
print(str(inspect.signature(f)))   # (a, b=2)
```

---

## Debugging checklist

*Debugging checklist in Debugging — what it is and when to use it.*

!!! tip "A systematic approach"
    1. Reproduce it reliably first.
    2. Read the **full** traceback — bottom line is the error, top is where it started.
    3. Narrow with `breakpoint()` or `print` at the boundary of good/bad state.
    4. Check assumptions with `assert` or by printing types, not just values.
    5. Fix the root cause, then add a test that would have caught it.

---

## Practice exercises

1. Use `breakpoint()` to step through a sorting algorithm and inspect variables at each iteration.
2. Set up logging with different levels for a multi-module program.
3. Debug a function by examining the call stack with `w` in pdb.
