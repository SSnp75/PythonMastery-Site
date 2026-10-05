---
title: Dataclasses
description: "@dataclass for clean data containers with less boilerplate"
---

# Dataclasses <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

---

## Basic usage

*Decorate a class with `@dataclass` and it auto-generates `__init__`, `__repr__`, and `__eq__` from your annotated fields — no boilerplate.*

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(3.0, 4.0)
print(p)               # Point(x=3.0, y=4.0)  — auto __repr__
print(p == Point(3.0, 4.0))   # True — auto __eq__
```

---

## Default values & fields

*Give fields defaults, and use `field(default_factory=...)` for mutable defaults like lists — never a bare `[]`, which would be shared across instances.*

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    tags: list = field(default_factory=list)   # mutable default
```

---

## Frozen (immutable)

*`frozen=True` makes instances read-only (and hashable) — ideal for value objects and dict keys where accidental mutation would be a bug.*

```python
@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float

c = Coordinate(40.7, -74.0)
c.lat = 0   # FrozenInstanceError!
```

---

## Post-init processing

*`__post_init__` runs after the generated `__init__` — use it to compute derived fields (marked `init=False`) from the supplied ones.*

```python
@dataclass
class Circle:
    radius: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = 3.14159 * self.radius ** 2
```

---

## Ordering & comparison

*`order=True` generates comparison methods that compare instances field-by-field as a tuple — so they sort naturally without a custom `__lt__`.*

`order=True` generates `__lt__`, `__le__`, etc., comparing fields as a tuple:

```python
from dataclasses import dataclass

@dataclass(order=True)
class Version:
    major: int
    minor: int

print(Version(1, 2) < Version(1, 5))   # True
print(sorted([Version(2, 0), Version(1, 9)]))
# [Version(major=1, minor=9), Version(major=2, minor=0)]
```

---

## `slots=True` — smaller, faster instances

*`slots=True` (3.10+) drops each instance's `__dict__` for lower memory and faster attribute access — valuable when you create many instances.*

Python 3.10+ can generate `__slots__`, which drops the per-instance `__dict__`:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(hasattr(p, "__dict__"))   # False — attributes live in slots
```

---

## Excluding a field from compare / repr

*Use `field(repr=False, compare=False)` to hide sensitive or irrelevant fields (like a password) from the string form and equality checks.*

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    password: str = field(repr=False, compare=False)

u = User("alice", "secret")
print(u)   # User(name='alice')  — password hidden from repr
print(u == User("alice", "different"))   # True — password ignored in ==
```

---

## Convert to dict / tuple

*`asdict` and `astuple` recursively convert a dataclass to plain containers — the easy path to JSON serialization or unpacking.*

```python
from dataclasses import dataclass, asdict, astuple

@dataclass
class Point:
    x: int
    y: int

p = Point(3, 4)
print(asdict(p))    # {'x': 3, 'y': 4}
print(astuple(p))   # (3, 4)
```

---

## Post-init validation (runnable)

*A runnable example using `__post_init__` to validate inputs and reject bad values — the standard place to enforce invariants on a dataclass.*

```python
from dataclasses import dataclass, field

@dataclass
class Circle:
    radius: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("radius must be non-negative")
        self.area = 3.14159 * self.radius ** 2

c = Circle(2)
print(round(c.area, 2))   # 12.57
```

---

## Practice exercises

1. Convert a regular class with `__init__`, `__repr__`, `__eq__` into a `@dataclass`.
2. Create a frozen `Color` dataclass with RGB values and a computed hex property.
3. Build a `@dataclass` with validation in `__post_init__`.
4. Use `order=True` to make a `Card` dataclass sortable by rank then suit.
5. Use `asdict` to serialize a nested dataclass to JSON.
