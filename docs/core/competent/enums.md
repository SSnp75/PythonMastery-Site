---
title: Enums
description: The enum module — Enum, IntEnum, auto(), Flag, StrEnum and when to use each
---

# Enums <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

---

An **enum** is a set of named constant values. It replaces magic strings/numbers with
self-documenting, type-safe members.

---

## Basic Enum

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)         # Color.RED
print(Color.RED.name)    # RED
print(Color.RED.value)   # 1
print(Color(2))          # Color.GREEN  (lookup by value)
print(Color["BLUE"])     # Color.BLUE   (lookup by name)
```

Members are singletons, so identity comparison works:

```python
from enum import Enum

class Color(Enum):
    RED = 1

print(Color.RED is Color.RED)   # True
print(Color.RED == Color.RED)   # True
```

---

## `auto()` for automatic values

```python
from enum import Enum, auto

class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

print([d.value for d in Direction])   # [1, 2, 3, 4]
```

---

## Iteration and membership

```python
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

print([s.name for s in Status])          # ['ACTIVE', 'INACTIVE']
print(Status.ACTIVE in Status)           # True
print(len(Status))                       # 2
```

---

## IntEnum — compares as an int

```python
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print(Priority.HIGH > Priority.LOW)   # True
print(Priority.MEDIUM + 1)            # 3  (behaves like an int)
```

---

## StrEnum (Python 3.11+) — compares as a str

```python
import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum

    class Env(StrEnum):
        DEV = "dev"
        PROD = "prod"

    print(Env.PROD == "prod")   # True
    print(Env.PROD.upper())     # PROD
```

---

## Flag — combinable bit flags

```python
from enum import Flag, auto

class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

access = Perm.READ | Perm.WRITE
print(Perm.READ in access)      # True
print(Perm.EXECUTE in access)   # False
print(access.value)             # 3  (READ=1 | WRITE=2)
```

---

## Methods on enums

Enums are classes — they can have methods:

```python
from enum import Enum

class Planet(Enum):
    EARTH = (5.976e24, 6.378e6)
    MARS = (6.421e23, 3.397e6)

    def __init__(self, mass, radius):
        self.mass = mass
        self.radius = radius

    def gravity(self):
        G = 6.67e-11
        return round(G * self.mass / self.radius ** 2, 2)

print(Planet.EARTH.gravity())   # 9.8
```

!!! tip "Which enum to use"
    - `Enum` — the default; values are opaque names.
    - `IntEnum` / `StrEnum` — when the member must interoperate as a plain int/str (e.g. JSON, DB).
    - `Flag` / `IntFlag` — combinable options (permissions, feature sets).
    - Add `@unique` to forbid duplicate values.

---

## Practice exercises

1. Model a traffic light as an `Enum` with a `next()` method cycling RED→GREEN→YELLOW→RED.
2. Use `IntEnum` for log levels and compare them with `>=`.
3. Use `Flag` to represent file permissions and test combined access.
4. Add `@unique` and confirm a duplicate value raises `ValueError`.
