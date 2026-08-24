---
title: Creational Patterns
description: Factory, Builder, Singleton, Prototype and Abstract Factory in Python
---

# Creational Patterns <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🏗️ Design Patterns · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="../core/competent/oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

---

## Factory Method

Create objects without specifying the exact class — let subclasses decide.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...

class EmailNotification(Notification):
    def __init__(self, recipient: str):
        self.recipient = recipient
    def send(self, message: str) -> None:
        print(f"  Email to {self.recipient}: {message}")

class SMSNotification(Notification):
    def __init__(self, phone: str):
        self.phone = phone
    def send(self, message: str) -> None:
        print(f"  SMS to {self.phone}: {message}")

class PushNotification(Notification):
    def __init__(self, device_id: str):
        self.device_id = device_id
    def send(self, message: str) -> None:
        print(f"  Push to {self.device_id}: {message}")

# Factory
def create_notification(channel: str, target: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel}")
    return factories[channel](target)

# Usage — caller doesn't know which class is created
notif = create_notification("email", "alice@example.com")
notif.send("Hello!")   # Email to alice@example.com: Hello!

notif = create_notification("sms", "+1234567890")
notif.send("Hi!")      # SMS to +1234567890: Hi!
```

---

## Builder

Construct complex objects step by step.

```python
from dataclasses import dataclass, field

@dataclass
class HttpRequest:
    method: str = "GET"
    url: str = ""
    headers: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    body: str | None = None
    timeout: int = 30

class RequestBuilder:
    def __init__(self):
        self._request = HttpRequest()

    def method(self, method: str) -> "RequestBuilder":
        self._request.method = method
        return self

    def url(self, url: str) -> "RequestBuilder":
        self._request.url = url
        return self

    def header(self, key: str, value: str) -> "RequestBuilder":
        self._request.headers[key] = value
        return self

    def param(self, key: str, value: str) -> "RequestBuilder":
        self._request.params[key] = value
        return self

    def body(self, data: str) -> "RequestBuilder":
        self._request.body = data
        return self

    def timeout(self, seconds: int) -> "RequestBuilder":
        self._request.timeout = seconds
        return self

    def build(self) -> HttpRequest:
        if not self._request.url:
            raise ValueError("URL is required")
        return self._request

# Usage — readable, flexible construction
request = (
    RequestBuilder()
    .method("POST")
    .url("https://api.example.com/users")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body('{"name": "Alice"}')
    .timeout(10)
    .build()
)
print(request)
# HttpRequest(method='POST', url='https://api.example.com/users', ...)
```

---

## Singleton

Ensure a class has only one instance.

```python
# Pythonic singleton using module-level instance
# config.py
class _Config:
    def __init__(self):
        self.debug = False
        self.database_url = ""
        self._loaded = False

    def load(self, path: str):
        if self._loaded:
            return
        import json
        with open(path) as f:
            data = json.load(f)
        self.debug = data.get("debug", False)
        self.database_url = data.get("database_url", "")
        self._loaded = True

config = _Config()   # THE singleton instance

# Usage (from anywhere):
# from config import config
# config.load("settings.json")
# print(config.database_url)
```

### Metaclass singleton (when you need stricter control):

```python
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url: str = "sqlite:///app.db"):
        self.url = url
        print(f"  Connected to {url}")

db1 = Database("postgres://localhost/mydb")   # Connected to postgres://...
db2 = Database("other://url")                  # no output — same instance
print(db1 is db2)   # True
print(db2.url)       # postgres://localhost/mydb
```

---

## Prototype (clone)

Create new objects by copying existing ones.

```python
import copy

class GameUnit:
    def __init__(self, name, hp, attack, defense, skills=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.skills = skills or []

    def clone(self):
        """Deep copy — independent from original."""
        return copy.deepcopy(self)

# Define prototypes
warrior_prototype = GameUnit("Warrior", hp=100, attack=15, defense=10, skills=["slash", "block"])
mage_prototype = GameUnit("Mage", hp=60, attack=25, defense=5, skills=["fireball", "heal"])

# Spawn units by cloning prototypes (cheaper than rebuilding)
unit1 = warrior_prototype.clone()
unit1.name = "Warrior #1"
unit1.skills.append("charge")

unit2 = warrior_prototype.clone()
unit2.name = "Warrior #2"

# Prototypes are independent
print(warrior_prototype.skills)   # ['slash', 'block'] — unchanged
print(unit1.skills)               # ['slash', 'block', 'charge']
print(unit2.skills)               # ['slash', 'block']
```

---

## Abstract Factory

Create families of related objects without specifying concrete classes.

```python
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class TextInput(ABC):
    @abstractmethod
    def render(self) -> str: ...

# Concrete products — Light theme
class LightButton(Button):
    def render(self): return "<button class='light'>Click</button>"

class LightTextInput(TextInput):
    def render(self): return "<input class='light' />"

# Concrete products — Dark theme
class DarkButton(Button):
    def render(self): return "<button class='dark'>Click</button>"

class DarkTextInput(TextInput):
    def render(self): return "<input class='dark' />"

# Abstract factory
class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_text_input(self) -> TextInput: ...

# Concrete factories
class LightThemeFactory(UIFactory):
    def create_button(self): return LightButton()
    def create_text_input(self): return LightTextInput()

class DarkThemeFactory(UIFactory):
    def create_button(self): return DarkButton()
    def create_text_input(self): return DarkTextInput()

# Client code — works with ANY factory
def build_form(factory: UIFactory):
    button = factory.create_button()
    text_input = factory.create_text_input()
    return f"{text_input.render()} {button.render()}"

# Switch themes by changing the factory
print(build_form(LightThemeFactory()))
# <input class='light' /> <button class='light'>Click</button>

print(build_form(DarkThemeFactory()))
# <input class='dark' /> <button class='dark'>Click</button>
```

---

## Practice Exercises

1. **Build a document factory** that creates PDFDocument, HTMLDocument, or MarkdownDocument based on file extension.
2. **Build a query builder** with chaining: `Query().select("name").from_("users").where("age > 18").limit(10).build()`
3. **Implement a connection pool** as a singleton with `acquire()` and `release()`.
4. **Use prototype** to clone complex configuration objects with modifications.
5. **Build an abstract factory** for database backends (SQLite, PostgreSQL, MySQL).
