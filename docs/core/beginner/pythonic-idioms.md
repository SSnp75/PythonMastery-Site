---
title: Pythonic Idioms
description: Write clean, idiomatic Python from day one
---

# Pythonic Idioms <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="data-structures/">Data Structures</a></span>
  </div>
</div>

---

## Unpacking

```python
# Tuple unpacking
a, b, c = 1, 2, 3

# Swap without temp variable
a, b = b, a

# Star unpacking
first, *rest = [1, 2, 3, 4, 5]
# first = 1, rest = [2, 3, 4, 5]

*head, last = [1, 2, 3, 4, 5]
# head = [1, 2, 3, 4], last = 5
```

---

## EAFP over LBYL

```python
# Bad — Look Before You Leap (LBYL)
if "key" in dictionary:
    value = dictionary["key"]

# Good — Easier to Ask Forgiveness than Permission (EAFP)
try:
    value = dictionary["key"]
except KeyError:
    value = "default"

# Even better
value = dictionary.get("key", "default")
```

---

## Use `enumerate`, not range(len())

```python
# Bad
for i in range(len(items)):
    print(i, items[i])

# Good
for i, item in enumerate(items):
    print(i, item)

# Start from 1
for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")
```

---

## Use `zip` to iterate in parallel

```python
# Bad
for i in range(len(names)):
    print(names[i], scores[i])

# Good
for name, score in zip(names, scores):
    print(name, score)
```

---

## Truthiness checks

```python
# Bad
if len(my_list) > 0:
if my_string != "":
if value == None:
if value == True:

# Good
if my_list:
if my_string:
if value is None:
if value is True:
```

---

## One-liner patterns

```python
# Conditional expression
label = "even" if x % 2 == 0 else "odd"

# Dictionary with get
name = config.get("name", "Anonymous")

# Join strings
", ".join(["apple", "banana", "cherry"])   # "apple, banana, cherry"

# any() and all()
has_negative = any(x < 0 for x in numbers)
all_positive = all(x > 0 for x in numbers)
```

---

## The Zen of Python

```python
import this
```

Key principles to remember:

- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Readability counts
- There should be one obvious way to do it

---

## Practice exercises

1. Rewrite a block of code using unpacking instead of index access.
2. Convert five `if key in dict` checks to use `.get()`.
3. Rewrite a `range(len())` loop to use `enumerate`.
4. Use `any()` and `all()` to validate a list of inputs.
