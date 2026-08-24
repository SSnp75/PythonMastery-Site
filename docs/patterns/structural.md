---
title: Structural Patterns
description: Adapter, Decorator, Facade, Proxy, Composite and Bridge in Python
---

# Structural Patterns <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🏗️ Design Patterns · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Adapter — make incompatible interfaces work together

```python
# Old payment system (can't change)
class LegacyPaymentGateway:
    def make_payment(self, amount_cents: int, card_number: str) -> dict:
        return {"status": "OK", "ref": "PAY-12345", "charged": amount_cents}

# New interface our app expects
class PaymentProcessor:
    def charge(self, amount_dollars: float, card: dict) -> dict:
        raise NotImplementedError

# Adapter bridges old → new
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self):
        self._gateway = LegacyPaymentGateway()

    def charge(self, amount_dollars: float, card: dict) -> dict:
        amount_cents = int(amount_dollars * 100)
        result = self._gateway.make_payment(amount_cents, card["number"])
        return {
            "success": result["status"] == "OK",
            "reference": result["ref"],
            "amount": amount_dollars,
        }

# Usage — app only sees the new interface
processor: PaymentProcessor = LegacyPaymentAdapter()
result = processor.charge(29.99, {"number": "4111111111111111"})
print(result)   # {'success': True, 'reference': 'PAY-12345', 'amount': 29.99}
```

---

## Decorator (structural) — add behavior dynamically

!!! note "Not the same as Python's `@decorator` syntax"
    The structural Decorator pattern wraps objects. Python's `@decorator` wraps functions. Same concept, different levels.

```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def write(self, data: str) -> None: ...
    @abstractmethod
    def read(self) -> str: ...

class FileDataSource(DataSource):
    def __init__(self, path: str):
        self.path = path
    def write(self, data: str):
        with open(self.path, "w") as f:
            f.write(data)
    def read(self) -> str:
        with open(self.path) as f:
            return f.read()

# Decorators — add encryption, compression, etc.
class EncryptedDataSource(DataSource):
    def __init__(self, wrapped: DataSource, key: str):
        self._wrapped = wrapped
        self._key = key
    def write(self, data: str):
        encrypted = self._encrypt(data)
        self._wrapped.write(encrypted)
    def read(self) -> str:
        return self._decrypt(self._wrapped.read())
    def _encrypt(self, data): return f"ENC[{data}]"   # simplified
    def _decrypt(self, data): return data[4:-1]

class CompressedDataSource(DataSource):
    def __init__(self, wrapped: DataSource):
        self._wrapped = wrapped
    def write(self, data: str):
        self._wrapped.write(f"ZIP[{data}]")   # simplified
    def read(self) -> str:
        raw = self._wrapped.read()
        return raw[4:-1]

# Stack decorators — encrypted + compressed file
source = CompressedDataSource(
    EncryptedDataSource(
        FileDataSource("secret.dat"),
        key="my-key"
    )
)
source.write("Hello, World!")
print(source.read())   # Hello, World! (transparently decrypted + decompressed)
```

---

## Facade — simplify complex subsystems

```python
class VideoFile:
    def __init__(self, path): self.path = path

class VideoCodec:
    def extract_audio(self, video): return f"audio_from_{video.path}"
    def extract_video(self, video): return f"video_from_{video.path}"

class AudioMixer:
    def mix(self, audio, effect): return f"mixed_{audio}_{effect}"

class VideoRenderer:
    def render(self, video, audio, format): return f"output.{format}"

# Facade — one simple method instead of 4 complex objects
class VideoConverter:
    """Simplified interface to the complex video processing subsystem."""

    def __init__(self):
        self._codec = VideoCodec()
        self._mixer = AudioMixer()
        self._renderer = VideoRenderer()

    def convert(self, input_path: str, output_format: str) -> str:
        video = VideoFile(input_path)
        audio = self._codec.extract_audio(video)
        video_stream = self._codec.extract_video(video)
        mixed_audio = self._mixer.mix(audio, "normalize")
        return self._renderer.render(video_stream, mixed_audio, output_format)

# Usage — simple!
converter = VideoConverter()
result = converter.convert("movie.avi", "mp4")
print(result)   # output.mp4
```

---

## Proxy — control access to an object

```python
import time

class ExpensiveDatabase:
    def query(self, sql: str) -> list:
        time.sleep(2)   # expensive!
        return [{"id": 1, "name": "Alice"}]

class CachingProxy:
    """Proxy that caches database queries."""

    def __init__(self, db: ExpensiveDatabase, ttl: int = 60):
        self._db = db
        self._cache: dict[str, tuple[float, list]] = {}
        self._ttl = ttl

    def query(self, sql: str) -> list:
        now = time.time()
        if sql in self._cache:
            cached_time, result = self._cache[sql]
            if now - cached_time < self._ttl:
                print("  Cache hit!")
                return result

        print("  Cache miss — querying DB...")
        result = self._db.query(sql)
        self._cache[sql] = (now, result)
        return result

# Usage
db = CachingProxy(ExpensiveDatabase(), ttl=300)
db.query("SELECT * FROM users")   # Cache miss — 2s
db.query("SELECT * FROM users")   # Cache hit! — instant
```

---

## Composite — tree structures with uniform interface

```python
from abc import ABC, abstractmethod

class FileSystemItem(ABC):
    @abstractmethod
    def get_size(self) -> int: ...
    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

class File(FileSystemItem):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
    def get_size(self) -> int:
        return self.size
    def display(self, indent=0):
        print(f"{'  ' * indent}📄 {self.name} ({self.size} bytes)")

class Directory(FileSystemItem):
    def __init__(self, name: str):
        self.name = name
        self.children: list[FileSystemItem] = []
    def add(self, item: FileSystemItem):
        self.children.append(item)
    def get_size(self) -> int:
        return sum(child.get_size() for child in self.children)
    def display(self, indent=0):
        print(f"{'  ' * indent}📁 {self.name} ({self.get_size()} bytes)")
        for child in self.children:
            child.display(indent + 1)

# Build tree
root = Directory("project")
src = Directory("src")
src.add(File("main.py", 1200))
src.add(File("utils.py", 800))
root.add(src)
root.add(File("README.md", 500))

root.display()
# 📁 project (2500 bytes)
#   📁 src (2000 bytes)
#     📄 main.py (1200 bytes)
#     📄 utils.py (800 bytes)
#   📄 README.md (500 bytes)

print(root.get_size())   # 2500 — works uniformly on files AND directories
```

---

## Practice Exercises

1. **Write an adapter** for a third-party logging library to match your app's logging interface.
2. **Stack decorators** — add logging, timing and retry to a data source.
3. **Build a facade** for a complex email system (templates, attachments, SMTP, tracking).
4. **Implement a lazy-loading proxy** for expensive database queries.
5. **Build a UI component tree** using Composite (Container with nested Widgets).
