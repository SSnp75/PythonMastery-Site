---
title: Iterators & Generators
description: yield, yield from, generator pipelines, itertools mastery
---

# Iterators & Generators <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../competent/comprehensions/">Comprehensions</a></span>
  </div>
</div>

---

## The Iterator Protocol

```python
class CountUp:
    """Custom iterator that counts from 1 to max."""
    def __init__(self, max_val):
        self.max = max_val
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current > self.max:
            raise StopIteration
        return self.current

for n in CountUp(5):
    print(n)   # 1, 2, 3, 4, 5
```

---

## Generators — the easy way

```python
def count_up(max_val):
    current = 1
    while current <= max_val:
        yield current      # pause here, resume on next()
        current += 1

for n in count_up(5):
    print(n)
```

---

## yield from

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # delegate to sub-generator
        else:
            yield item

list(flatten([1, [2, 3], [4, [5, 6]]]))
# [1, 2, 3, 4, 5, 6]
```

---

## Generator Pipelines

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

def filter_comments(lines):
    for line in lines:
        if not line.startswith("#"):
            yield line

def to_upper(lines):
    for line in lines:
        yield line.upper()

# Compose the pipeline — lazy, memory-efficient
pipeline = to_upper(filter_comments(read_lines("config.txt")))
for line in pipeline:
    print(line)
```

---

## itertools highlights

```python
from itertools import chain, islice, groupby, product, permutations

# chain — concatenate iterables
list(chain([1, 2], [3, 4]))   # [1, 2, 3, 4]

# islice — slice any iterable
list(islice(count_up(100), 5))   # [1, 2, 3, 4, 5]

# groupby — group consecutive equal elements
data = sorted(students, key=lambda s: s["grade"])
for grade, group in groupby(data, key=lambda s: s["grade"]):
    print(f"Grade {grade}: {list(group)}")
```

---

## Practice exercises

1. Write a generator `fibonacci()` that yields Fibonacci numbers forever.
2. Build a 3-stage pipeline: read CSV → filter rows → transform → output.
3. Implement `flatten()` that handles arbitrarily nested lists.
4. Use `itertools.groupby` to group words by their first letter.
