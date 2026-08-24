---
title: Comprehensions
description: List, dict, set and generator comprehensions
---

# Comprehensions <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## List comprehension

```python
# [expression for item in iterable if condition]
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
words   = [w.upper() for w in sentence.split() if len(w) > 3]
```

---

## Dict comprehension

```python
# {key_expr: value_expr for item in iterable}
scores = {"Alice": 95, "Bob": 87, "Charlie": 72}
passed = {k: v for k, v in scores.items() if v >= 80}
# {'Alice': 95, 'Bob': 87}
```

---

## Set comprehension

```python
unique_lengths = {len(w) for w in words}
```

---

## Generator expression

```python
# Like list comp but with () — lazy evaluation
total = sum(x**2 for x in range(1000000))   # no list in memory
```

---

## Nested comprehensions

```python
# Flatten a matrix
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [n for row in matrix for n in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Create a matrix
grid = [[0 for _ in range(3)] for _ in range(3)]
```

!!! warning "Readability limit"
    If a comprehension gets hard to read, use a regular loop. Comprehensions should clarify, not obfuscate.

---

## Practice exercises

1. Use a dict comprehension to invert a dictionary (swap keys and values).
2. Use a nested list comprehension to generate a multiplication table.
3. Use a generator expression with `sum()` to calculate the sum of all primes below 10000.
