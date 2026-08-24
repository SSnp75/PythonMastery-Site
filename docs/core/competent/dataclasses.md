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

```python
@dataclass
class Circle:
    radius: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = 3.14159 * self.radius ** 2
```

---

## Practice exercises

1. Convert a regular class with `__init__`, `__repr__`, `__eq__` into a `@dataclass`.
2. Create a frozen `Color` dataclass with RGB values and a computed hex property.
3. Build a `@dataclass` with validation in `__post_init__`.
