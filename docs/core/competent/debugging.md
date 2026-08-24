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

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

logger.debug("Variable x = %s", x)
logger.info("Processing started")
logger.warning("Disk space low")
logger.error("Failed to connect")
logger.critical("System crash!")
```

---

## Practice exercises

1. Use `breakpoint()` to step through a sorting algorithm and inspect variables at each iteration.
2. Set up logging with different levels for a multi-module program.
3. Debug a function by examining the call stack with `w` in pdb.
