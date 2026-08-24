---
title: Standard Library
description: Essential built-in modules — collections, datetime, pathlib, re, functools, itertools, subprocess
---

# Standard Library <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="modules-packages/">Modules & Packages</a></span>
  </div>
</div>

---

## collections

### Counter — count anything

```python
from collections import Counter

words = "the cat sat on the mat the cat".split()
c = Counter(words)
print(c)                    # Counter({'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})
print(c.most_common(2))     # [('the', 3), ('cat', 2)]
print(c['the'])             # 3
print(c['dog'])             # 0 (no KeyError!)

# Arithmetic
c2 = Counter("aaabbc")
c3 = Counter("abccdd")
print(c2 + c3)   # Counter({'a': 4, 'b': 3, 'c': 3, 'd': 2})
print(c2 - c3)   # Counter({'a': 2, 'b': 1})  — only positive counts
```

### defaultdict — dict with auto-creation

```python
from collections import defaultdict

# Group items
words = ["apple", "ant", "banana", "avocado", "blueberry"]
by_letter = defaultdict(list)
for w in words:
    by_letter[w[0]].append(w)

print(dict(by_letter))
# {'a': ['apple', 'ant', 'avocado'], 'b': ['banana', 'blueberry']}

# Count occurrences (alternative to Counter)
counts = defaultdict(int)
for w in "hello world".split():
    counts[w] += 1

# Nested dicts
tree = defaultdict(lambda: defaultdict(list))
tree["fruits"]["red"].append("apple")
tree["fruits"]["yellow"].append("banana")
```

### deque — fast double-ended queue

```python
from collections import deque

d = deque([1, 2, 3, 4, 5])

d.appendleft(0)     # O(1) — list.insert(0, x) is O(n)!
d.append(6)         # O(1)
d.popleft()         # O(1) — list.pop(0) is O(n)!
d.pop()             # O(1)

# Rotate
d.rotate(2)         # [4, 5, 1, 2, 3]
d.rotate(-1)        # [5, 1, 2, 3, 4]

# Fixed-size buffer (oldest items drop off)
recent = deque(maxlen=3)
for i in range(10):
    recent.append(i)
print(list(recent))   # [7, 8, 9]  — only last 3 kept
```

### namedtuple — lightweight immutable class

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)      # 3 4
print(p[0], p[1])    # 3 4  — also indexable
print(p._asdict())   # {'x': 3, 'y': 4}

# With defaults (Python 3.6.1+)
Config = namedtuple("Config", ["host", "port", "debug"], defaults=["localhost", 8080, False])
c = Config()
print(c)   # Config(host='localhost', port=8080, debug=False)
```

### OrderedDict — insertion-ordered dict (mostly redundant since 3.7)

```python
from collections import OrderedDict

# Still useful for: move_to_end, equality considers order
od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")        # moves 'a' to the end
od.move_to_end("c", last=False)   # moves 'c' to the front
print(list(od.keys()))      # ['c', 'b', 'a']

# LRU cache implementation
class LRU(OrderedDict):
    def __init__(self, maxsize=128):
        super().__init__()
        self.maxsize = maxsize

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)   # recently accessed → end
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
```

### ChainMap — merged view of multiple dicts

```python
from collections import ChainMap

defaults = {"color": "red", "size": "medium", "weight": "light"}
user_prefs = {"color": "blue"}
cli_args = {"size": "large"}

config = ChainMap(cli_args, user_prefs, defaults)
print(config["color"])    # blue  (found in user_prefs)
print(config["size"])     # large (found in cli_args)
print(config["weight"])   # light (found in defaults)
```

---

## datetime

```python
from datetime import datetime, date, time, timedelta, timezone

# Current time
now = datetime.now()
utc = datetime.now(timezone.utc)
today = date.today()

print(now)     # 2026-08-23 20:15:30.123456
print(utc)     # 2026-08-23 14:45:30.123456+00:00
print(today)   # 2026-08-23

# Creating specific dates/times
d = date(2025, 12, 25)
t = time(14, 30, 0)
dt = datetime(2025, 12, 25, 14, 30, 0)

# Formatting
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 2026-08-23 20:15:30
print(now.strftime("%B %d, %Y"))            # August 23, 2026
print(now.strftime("%I:%M %p"))             # 08:15 PM

# Parsing
parsed = datetime.strptime("2025-06-15 09:30", "%Y-%m-%d %H:%M")
print(parsed)   # 2025-06-15 09:30:00

# Arithmetic
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(weeks=1)
two_hours_later = now + timedelta(hours=2)

# Difference
d1 = date(2026, 1, 1)
d2 = date(2026, 12, 31)
diff = d2 - d1
print(diff.days)   # 364

# Timezone-aware
from datetime import timezone
utc_time = datetime.now(timezone.utc)
ist = timezone(timedelta(hours=5, minutes=30))
ist_time = utc_time.astimezone(ist)
```

### Common formatting codes

| Code | Meaning | Example |
|---|---|---|
| `%Y` | 4-digit year | 2026 |
| `%m` | Month (01-12) | 08 |
| `%d` | Day (01-31) | 23 |
| `%H` | Hour 24h (00-23) | 20 |
| `%I` | Hour 12h (01-12) | 08 |
| `%M` | Minute (00-59) | 15 |
| `%S` | Second (00-59) | 30 |
| `%p` | AM/PM | PM |
| `%A` | Weekday name | Sunday |
| `%B` | Month name | August |

---

## pathlib — object-oriented filesystem

```python
from pathlib import Path

# Navigation
home = Path.home()
project = Path("src") / "myapp" / "main.py"
print(project)          # src/myapp/main.py
print(project.parent)   # src/myapp
print(project.name)     # main.py
print(project.stem)     # main
print(project.suffix)   # .py

# Querying
path = Path("some_file.txt")
print(path.exists())
print(path.is_file())
print(path.is_dir())
print(path.stat().st_size)   # file size in bytes

# Reading/Writing
content = Path("data.txt").read_text(encoding="utf-8")
Path("output.txt").write_text("hello", encoding="utf-8")

# File operations
path.rename("new_name.txt")
path.unlink()               # delete file
Path("newdir").mkdir(parents=True, exist_ok=True)

# Globbing
for py_file in Path("src").glob("**/*.py"):   # recursive
    print(py_file)

for csv in Path(".").glob("*.csv"):   # current directory only
    print(csv)

# Resolving
relative = Path("../other/file.txt")
absolute = relative.resolve()
print(absolute)   # /full/path/to/other/file.txt
```

---

## re — regular expressions

```python
import re

text = "Contact us at support@example.com or sales@company.org"

# Find all emails
emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
print(emails)   # ['support@example.com', 'sales@company.org']

# Search (first match)
match = re.search(r"(\w+)@(\w+)\.(\w+)", text)
if match:
    print(match.group(0))   # support@example.com  (full match)
    print(match.group(1))   # support (first group)
    print(match.group(2))   # example
    print(match.groups())   # ('support', 'example', 'com')

# Substitute
cleaned = re.sub(r"\d{3}-\d{4}", "XXX-XXXX", "Call 555-1234 or 555-5678")
print(cleaned)   # Call XXX-XXXX or XXX-XXXX

# Split
parts = re.split(r"[;,\s]+", "one, two; three   four")
print(parts)   # ['one', 'two', 'three', 'four']

# Compile for reuse (faster in loops)
pattern = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
phones = pattern.findall("Call 123-456-7890 or 098-765-4321")

# Named groups
m = re.match(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2026-08-23")
print(m.group("year"))    # 2026
print(m.groupdict())      # {'year': '2026', 'month': '08', 'day': '23'}

# Flags
case_insensitive = re.findall(r"python", "Python PYTHON python", re.IGNORECASE)
print(case_insensitive)   # ['Python', 'PYTHON', 'python']
```

### Common patterns

| Pattern | Matches |
|---|---|
| `\d+` | One or more digits |
| `\w+` | Word characters (letters, digits, underscore) |
| `\s+` | Whitespace |
| `.*?` | Any chars (non-greedy) |
| `^...$` | Full line match |
| `\b` | Word boundary |
| `(?:...)` | Non-capturing group |
| `(?P<name>...)` | Named group |
| `(?=...)` | Lookahead |
| `(?<=...)` | Lookbehind |

---

## functools

```python
from functools import lru_cache, partial, reduce, wraps, total_ordering

# lru_cache — memoization
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))   # 354224848179261915075 (instant!)
print(fibonacci.cache_info())   # hits, misses, maxsize, currsize

# partial — freeze some arguments
from operator import mul
double = partial(mul, 2)
print(double(5))   # 10
print(list(map(double, [1, 2, 3])))   # [2, 4, 6]

# reduce — fold a sequence
total = reduce(lambda a, b: a + b, [1, 2, 3, 4, 5])
print(total)   # 15

# total_ordering — generate comparison methods
@total_ordering
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
    def __eq__(self, other):
        return self.grade == other.grade
    def __lt__(self, other):
        return self.grade < other.grade

# Now has __le__, __gt__, __ge__ automatically
```

---

## itertools

```python
from itertools import (
    chain, islice, cycle, repeat, count,
    product, permutations, combinations,
    groupby, accumulate, starmap, takewhile, dropwhile
)

# chain — concatenate iterables
list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]

# islice — slice any iterable
list(islice(count(10), 5))   # [10, 11, 12, 13, 14]

# cycle — repeat forever
colors = cycle(["red", "green", "blue"])
print([next(colors) for _ in range(7)])
# ['red', 'green', 'blue', 'red', 'green', 'blue', 'red']

# product — cartesian product
list(product("AB", "12"))   # [('A','1'), ('A','2'), ('B','1'), ('B','2')]

# combinations
list(combinations("ABCD", 2))
# [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')]

# permutations
list(permutations("ABC", 2))
# [('A','B'), ('A','C'), ('B','A'), ('B','C'), ('C','A'), ('C','B')]

# groupby (data must be sorted by key!)
data = [("A", 1), ("A", 2), ("B", 3), ("B", 4), ("C", 5)]
for key, group in groupby(data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")
# A: [('A', 1), ('A', 2)]
# B: [('B', 3), ('B', 4)]
# C: [('C', 5)]

# accumulate — running totals
list(accumulate([1, 2, 3, 4, 5]))   # [1, 3, 6, 10, 15]

# takewhile / dropwhile
list(takewhile(lambda x: x < 5, [1, 3, 5, 2, 1]))   # [1, 3]
list(dropwhile(lambda x: x < 5, [1, 3, 5, 2, 1]))   # [5, 2, 1]
```

---

## subprocess — run external commands

```python
import subprocess

# Simple command
result = subprocess.run(
    ["git", "status"],
    capture_output=True,
    text=True,
    check=True,         # raises CalledProcessError if exit code != 0
    timeout=30,         # timeout in seconds
)
print(result.stdout)
print(result.returncode)   # 0

# With shell (be careful with user input!)
result = subprocess.run(
    "echo hello && echo world",
    shell=True,
    capture_output=True,
    text=True,
)
print(result.stdout)   # hello\nworld\n

# Piping
p1 = subprocess.Popen(["cat", "file.txt"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "error"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = p2.communicate()[0]
```

---

## shutil — high-level file operations

```python
import shutil

# Copy
shutil.copy("src.txt", "dst.txt")           # copy file
shutil.copy2("src.txt", "dst.txt")          # copy with metadata
shutil.copytree("src_dir", "dst_dir")       # copy entire directory

# Move
shutil.move("old_path", "new_path")

# Delete
shutil.rmtree("directory")   # delete directory tree (careful!)

# Archive
shutil.make_archive("backup", "zip", "my_folder")   # creates backup.zip
shutil.unpack_archive("backup.zip", "extracted/")

# Disk usage
total, used, free = shutil.disk_usage("/")
print(f"Free: {free // (1024**3)} GB")
```

---

## os & sys essentials

```python
import os, sys

# Environment
print(os.environ.get("PATH"))
os.environ["MY_VAR"] = "value"

# System info
print(os.cpu_count())         # number of CPUs
print(os.getpid())            # current process ID
print(sys.platform)           # 'win32', 'linux', 'darwin'
print(sys.version)            # '3.13.15 ...'
print(sys.argv)               # command-line arguments

# Working directory
print(os.getcwd())
os.chdir("/tmp")
```

---

## Practice Exercises

1. **Use `Counter`** to find the 10 most common words in a text file.
2. **Build an LRU cache** using `OrderedDict` with `maxsize` parameter.
3. **Write a log parser** using `re` that extracts timestamps, levels and messages.
4. **Use `itertools.groupby`** to group a list of records by date.
5. **Use `pathlib`** to find all files larger than 1MB in a directory tree.
6. **Use `subprocess`** to run `git log --oneline -10` and parse the output into a list of dicts.
7. **Implement a simple scheduler** using `datetime` + `timedelta` that runs functions at specified intervals.
