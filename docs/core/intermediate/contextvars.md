---
title: Context Variables
description: contextvars for request-scoped state that is safe across threads and asyncio tasks
---

# Context Variables <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="../../systems/proficient/asyncio/">Asyncio</a></span>
  </div>
</div>

---

`contextvars` (Python 3.7+) provides variables whose values are **local to a logical
context** — a thread or an asyncio task. They solve the problem of passing request-scoped
data (request IDs, the current user, locale) without threading it through every function
argument, and unlike globals they don't leak between concurrent tasks.

---

## Basic get / set

```python
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")

print(request_id.get())        # -  (the default)
request_id.set("abc123")
print(request_id.get())        # abc123
```

---

## Tokens and reset

`set()` returns a `Token` that restores the previous value — the basis for scoped overrides:

```python
from contextvars import ContextVar

level = ContextVar("level", default="INFO")

token = level.set("DEBUG")
print(level.get())    # DEBUG
level.reset(token)
print(level.get())    # INFO  (restored)
```

---

## Why not just a global?

A plain global is shared by every task. A `ContextVar` gives each asyncio task its own
value, so concurrent requests don't clobber each other.

```python
import asyncio
from contextvars import ContextVar

user = ContextVar("user")

async def handle(name):
    user.set(name)
    await asyncio.sleep(0.01)      # yield to the event loop
    return user.get()              # still *this* task's value

async def main():
    return await asyncio.gather(handle("alice"), handle("bob"))

print(asyncio.run(main()))   # ['alice', 'bob']  — no cross-talk
```

With a global, the interleaving `await` would let one task overwrite the other.

---

## Running inside a copied context

`copy_context()` snapshots the current values and runs a callable in that isolated copy —
changes inside don't escape:

```python
import contextvars

v = contextvars.ContextVar("v", default=0)

def bump_and_read():
    v.set(99)
    return v.get()

ctx = contextvars.copy_context()
print(ctx.run(bump_and_read))   # 99  (inside the copied context)
print(v.get())                  # 0   (outer context unchanged)
```

---

## A practical logging-context pattern

```python
from contextvars import ContextVar

correlation_id = ContextVar("correlation_id", default="none")

def log(message):
    return f"[{correlation_id.get()}] {message}"

correlation_id.set("req-42")
print(log("processing"))   # [req-42] processing
```

Middleware sets the id once per request; every log call deep in the stack picks it up
automatically.

!!! tip "contextvars vs threading.local"
    `threading.local` is per-thread only. `ContextVar` is per-thread **and** per-asyncio-task,
    and it propagates correctly across `await` — making it the right tool for async apps.

---

## Practice exercises

1. Create a `locale` ContextVar and a function that formats a greeting using its value.
2. Use a token to temporarily override a setting inside a `with`-style helper, then restore it.
3. Launch three asyncio tasks that each set and read their own `ContextVar` value.
4. Use `copy_context().run()` to call a function without letting its context changes leak out.
