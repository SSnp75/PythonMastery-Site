---
title: "Code Snippets"
description: Reusable, copy-paste Python snippets for common tasks
---

# Code Snippets <span class="pm-badge pm-badge-beginner">Reference</span>

<div class="pm-topic-header">
  <strong>📚 Reference</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Quick reference</span>
    <span>📚 Copy, paste, adapt</span>
  </div>
</div>

---

A curated collection of small, reusable Python snippets for tasks you hit again and again. Every snippet here uses the **standard library** and has been verified to run.

---

## Files & paths

```python
from pathlib import Path

# Read / write a whole text file
text = Path("file.txt").read_text(encoding="utf-8")
Path("out.txt").write_text(text, encoding="utf-8")

# All .py files recursively
py_files = list(Path(".").rglob("*.py"))

# Ensure a directory exists (no error if it does)
Path("logs").mkdir(parents=True, exist_ok=True)

# File size in KB
kb = Path("file.txt").stat().st_size / 1024
```

## Dictionaries

```python
# Merge two dicts (right wins on conflict) — Python 3.9+
merged = {"a": 1} | {"b": 2, "a": 9}     # {'a': 9, 'b': 2}

# Invert a dict
inv = {v: k for k, v in {"a": 1, "b": 2}.items()}   # {1: 'a', 2: 'b'}

# Count occurrences
from collections import Counter
counts = Counter("mississippi")          # {'i': 4, 's': 4, 'p': 2, 'm': 1}
top2 = counts.most_common(2)             # [('i', 4), ('s', 4)]

# Group items by a key
from collections import defaultdict
groups = defaultdict(list)
for word in ["apple", "avocado", "banana"]:
    groups[word[0]].append(word)         # {'a': ['apple','avocado'], 'b': ['banana']}
```

## Lists & iterables

```python
# Flatten one level
nested = [[1, 2], [3, 4]]
flat = [x for row in nested for x in row]      # [1, 2, 3, 4]

# Deduplicate, preserving order
items = [3, 1, 3, 2, 1]
unique = list(dict.fromkeys(items))            # [3, 1, 2]

# Chunk a list into size-n pieces
def chunk(seq, n):
    return [seq[i:i+n] for i in range(0, len(seq), n)]
chunk([1,2,3,4,5], 2)                          # [[1,2],[3,4],[5]]

# Pair each item with its index
for i, val in enumerate(["a", "b"], start=1):
    ...                                        # 1 a, 2 b

# Combine two lists
list(zip([1, 2], ["a", "b"]))                  # [(1,'a'), (2,'b')]
```

## Strings

```python
# Reverse a string
"hello"[::-1]                                  # 'olleh'

# Check palindrome
s = "racecar"
is_pal = s == s[::-1]                          # True

# Split on any whitespace, drop empties
"a  b\tc".split()                              # ['a', 'b', 'c']

# Join with a separator
", ".join(["a", "b", "c"])                     # 'a, b, c'

# Slugify-ish (basic)
import re
re.sub(r"[^a-z0-9]+", "-", "Hello World!".lower()).strip("-")   # 'hello-world'
```

## Dates & time

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)               # timezone-aware "now"
stamp = now.strftime("%Y-%m-%d %H:%M:%S")      # formatted string
tomorrow = now + timedelta(days=1)
parsed = datetime.strptime("2026-01-15", "%Y-%m-%d")
```

## JSON

```python
import json
from pathlib import Path

data = json.loads(Path("config.json").read_text(encoding="utf-8"))
Path("out.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
```

## Functional helpers

```python
from functools import reduce, lru_cache

# Sum via reduce (usually just use sum())
reduce(lambda a, b: a + b, [1, 2, 3, 4])       # 10

# Memoize an expensive/recursive function
@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
fib(30)                                         # 832040 (fast, cached)
```

## Timing a block

```python
import time

start = time.perf_counter()
# ... work ...
elapsed_ms = (time.perf_counter() - start) * 1000
```

---

!!! tip "Verified snippets"
    Every snippet on this page uses only the standard library and has been run to confirm it works. Copy freely. For domain-specific snippets (NumPy, web, etc.), see the relevant track pages.

---

## Related

- [Cheat Sheets](cheatsheets.md) — syntax and library quick reference
- [Glossary](glossary.md) — terminology
- [Pythonic Idioms](../core/beginner/pythonic-idioms.md) — the *why* behind many of these
