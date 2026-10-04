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

## Conditional expression inside the output

Put a ternary in the **expression** part to transform (not filter):

```python
labels = ["even" if x % 2 == 0 else "odd" for x in range(4)]
print(labels)   # ['even', 'odd', 'even', 'odd']
```

Filtering (`if` at the end) and transforming (`if/else` up front) can combine:

```python
result = [x * 2 for x in range(10) if x % 3 == 0]
print(result)   # [0, 6, 12, 18]
```

---

## Invert / transform a dict

```python
scores = {"Alice": 95, "Bob": 87}
inverted = {v: k for k, v in scores.items()}
print(inverted)   # {95: 'Alice', 87: 'Bob'}
```

---

## Walrus operator in comprehensions

Reuse a computed value without recomputing it (Python 3.8+):

```python
def expensive(x):
    return x * x

results = [y for x in range(6) if (y := expensive(x)) > 10]
print(results)   # [16, 25]
```

---

## The classic nested-loop ordering gotcha

`for` clauses read **left to right**, same as nested loops:

```python
pairs = [(x, y) for x in [1, 2] for y in ["a", "b"]]
print(pairs)   # [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
```

---

## Generator vs list memory

```python
import sys

list_comp = [x for x in range(1000)]
gen_exp   = (x for x in range(1000))
print(sys.getsizeof(list_comp) > sys.getsizeof(gen_exp))   # True
```

A generator holds one item at a time; the list holds all 1000.

---

## Practice exercises

1. Use a dict comprehension to invert a dictionary (swap keys and values).
2. Use a nested list comprehension to generate a multiplication table.
3. Use a generator expression with `sum()` to calculate the sum of all primes below 10000.
4. Use the walrus operator in a comprehension to keep only values whose square root is an integer.
5. Build a dict comprehension that maps each word in a sentence to its length.
