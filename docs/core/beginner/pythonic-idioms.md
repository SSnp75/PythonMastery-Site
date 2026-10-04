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

!!! info "When you'd use this"
    Write clean, idiomatic Python from day one.

    Apply these idioms whenever you write Python: unpacking, EAFP, `enumerate`/`zip`, and truthiness checks make code shorter, clearer, and more idiomatic.


## Unpacking

*Assign multiple names from a sequence at once, swap without a temp, or capture "the rest" with `*`. Cleaner than index-by-index access.*

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

*Pythonic style: try the operation and handle the exception, rather than pre-checking. Avoids race conditions and is often clearer — but `dict.get` is cleaner still for defaults.*

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

*When you need both index and value, `enumerate` is clearer and less error-prone than indexing. Pass `start=1` for human-friendly numbering.*

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

*Walk two or more sequences together without index bookkeeping — pairing names with scores, keys with values, etc.*

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

*Empty containers and `0`/`""`/`None` are falsy — test them directly. Use `is None` for None and `is True` for identity, not `==`.*

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

*A toolkit of concise expressions — ternaries, `dict.get` defaults, `join`, `any`/`all` — that replace multi-line boilerplate when the logic is simple.*

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

*Python's guiding design aphorisms (PEP 20). Run `import this` anytime you need a reminder of what "Pythonic" means.*

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
