---
title: Pattern Matching
description: Structural pattern matching with match/case (PEP 634) — literals, sequences, mappings, classes, guards and captures
---

# Pattern Matching <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="../beginner/control-flow/">Control Flow</a></span>
  </div>
</div>

---

`match`/`case` (Python 3.10+, PEP 634) is **structural** pattern matching — it matches the
*shape* of data and can bind parts of it to names. It is far more than a C-style switch.

---

## Literal matching

*Literal matching in Pattern Matching — what it is and when to use it.*

```python
def http_label(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:                     # wildcard — the "default"
            return "Unknown"

print(http_label(200))   # OK
print(http_label(999))   # Unknown
```

---

## Or-patterns and value capture

*Or-patterns and value capture in Pattern Matching — what it is and when to use it.*

```python
def kind(ch):
    match ch:
        case "a" | "e" | "i" | "o" | "u":
            return "vowel"
        case letter if letter.isalpha():
            return "consonant"
        case _:
            return "other"

print(kind("e"))   # vowel
print(kind("z"))   # consonant
print(kind("7"))   # other
```

---

## Sequence patterns (with capture & star)

*Sequence patterns (with capture & star) in Pattern Matching — what it is and when to use it.*

```python
def describe(seq):
    match seq:
        case []:
            return "empty"
        case [x]:
            return f"one: {x}"
        case [first, *rest]:
            return f"first={first}, rest={rest}"

print(describe([]))          # empty
print(describe([42]))        # one: 42
print(describe([1, 2, 3]))   # first=1, rest=[2, 3]
```

---

## Mapping patterns

*Mapping patterns in Pattern Matching — what it is and when to use it.*

Match specific keys in a dict; extra keys are ignored.

```python
def route(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at ({x}, {y})"
        case {"type": "key", "key": k}:
            return f"key {k}"
        case _:
            return "unhandled"

print(route({"type": "click", "x": 10, "y": 20}))   # click at (10, 20)
print(route({"type": "key", "key": "Enter"}))        # key Enter
```

---

## Class patterns

*Class patterns in Pattern Matching — what it is and when to use it.*

Destructure objects by type and attributes. Dataclasses work especially well.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def quadrant(p):
    match p:
        case Point(x=0, y=0):
            return "origin"
        case Point(x=0):
            return "on y-axis"
        case Point(y=0):
            return "on x-axis"
        case Point(x=x, y=y) if x > 0 and y > 0:
            return "Q1"
        case _:
            return "elsewhere"

print(quadrant(Point(0, 0)))   # origin
print(quadrant(Point(3, 4)))   # Q1
print(quadrant(Point(0, 5)))   # on y-axis
```

---

## Guards

*Guards in Pattern Matching — what it is and when to use it.*

A `if` after a pattern adds an extra condition that must also hold:

```python
def classify(n):
    match n:
        case int() if n < 0:
            return "negative int"
        case int():
            return "non-negative int"
        case _:
            return "not an int"

print(classify(-3))     # negative int
print(classify(5))      # non-negative int
print(classify("x"))    # not an int
```

!!! tip "When to reach for match"
    Use `match` when you branch on the **structure** of data (parsing, ASTs, event handling,
    command dispatch). For a simple value lookup, a dict is still cleaner than a `match`.

---

## Practice exercises

1. Write a `match` that parses a `["move", x, y]` / `["rotate", deg]` command list.
2. Match an HTTP response dict and extract `status` and `body`, defaulting body to `""`.
3. Destructure a nested point `Point(Point(0,0), Point(x,y))` with class patterns.
4. Use a guard to match only even integers.
