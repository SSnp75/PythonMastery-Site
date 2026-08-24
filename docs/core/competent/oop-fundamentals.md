---
title: OOP Fundamentals
description: Classes, inheritance, polymorphism, encapsulation and abstract base classes
---

# OOP Fundamentals <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisite: <a href="modules-packages/">Modules & Packages</a></span>
  </div>
</div>

---

## Classes & Objects

```python
class Dog:
    species = "Canis familiaris"   # class variable

    def __init__(self, name, age):
        self.name = name           # instance variable
        self.age  = age

    def bark(self):
        return f"{self.name} says Woof!"

rex = Dog("Rex", 5)
print(rex.bark())        # Rex says Woof!
print(Dog.species)       # Canis familiaris
```

---

## Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"
```

---

## super()

```python
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)   # call parent
        self.doors = doors
```

---

## Encapsulation

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance        # convention: "private"

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
```

---

## Polymorphism

```python
animals = [Cat("Whiskers"), Dog("Rex")]
for animal in animals:
    print(animal.speak())   # each calls its own version
```

---

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius
```

---

## Dunder Methods

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return int((self.x**2 + self.y**2) ** 0.5)
```

---

## Practice exercises

1. Build a `Library` system with `Book`, `Member` and loan tracking.
2. Create a shape hierarchy with `Circle`, `Rectangle`, `Triangle` all implementing `area()` and `perimeter()`.
3. Implement `__add__`, `__sub__`, `__eq__` for a `Money` class with currency conversion.
4. Write an abstract `Database` class with concrete `SQLiteDB` and `PostgresDB` implementations.
