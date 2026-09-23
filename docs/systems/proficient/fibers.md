---
title: "Fibers"
description: Stackful coroutines and how they differ from asyncio's stackless model
---

# Fibers <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="green-threads.md">Green Threads</a>, <a href="../../core/intermediate/iterators-generators.md">Generators</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What a fiber is
- [x] Stackful vs stackless coroutines
- [x] How fibers differ from asyncio
- [x] Generator-based cooperative switching (tested)
- [x] The Python landscape

A **fiber** is a lightweight, cooperatively-scheduled unit of execution with its **own stack** that can be suspended and resumed at any point in its call chain. Fibers are close cousins of [green threads](green-threads.md) — the distinguishing detail is being *stackful*. The generator switching demo here is **run-verified**.

---

## Stackful vs stackless

This is the crux of the topic:

- **Stackful coroutine (fiber)** — has its own full call stack. It can suspend from *anywhere*, even deep inside nested function calls, and resume exactly there. You can `yield`/switch from a helper function three levels down.
- **Stackless coroutine (asyncio)** — does **not** have its own stack. It can only suspend at explicit `await` points in the coroutine itself. To suspend inside a called function, that function must *also* be a coroutine and you must `await` it all the way up.

```
   Stackful (fiber):                  Stackless (asyncio):
   coro()                             async def coro():
     └─ helper()                        await inner()      ← must await
          └─ deep()  ← can switch         # inner must be async too
             HERE directly                # switch only at await
```

The practical difference: fibers let *any* code suspend without every caller knowing about it; stackless coroutines require the `async`/`await` "coloring" to propagate up the call chain (the famous "function color" problem).

---

## Cooperative switching with generators (tested)

Python generators are a *stackless* coroutine primitive — they suspend only at their own `yield`, not inside called functions. We can still model cooperative multitasking with them. Runnable:

```python
def fiber(name, steps, log):
    for i in range(steps):
        log.append(f"{name}:{i}")
        yield                       # suspend at this point

def schedule(fibers):
    log = []
    active = list(fibers)
    while active:
        remaining = []
        for f in active:
            try:
                next(f)             # resume until next yield
                remaining.append(f)
            except StopIteration:
                pass
        active = remaining
    return log

log = []
schedule([fiber("A", 2, log), fiber("B", 3, log)])
print(log)
```

Output:

```text
['A:0', 'B:0', 'A:1', 'B:1', 'B:2']
```

The fibers interleave cooperatively. But notice the limit: a generator can only `yield` from its *own* body — try to suspend from a helper function it calls and you can't (without that helper also being a generator). That's exactly the *stackless* constraint. A true fiber library removes this limit with its own stack.

---

## The Python landscape

Python's built-in tools are mostly stackless:

| Tool | Stackful? | Notes |
|---|---|---|
| **Generators** | No (stackless) | `yield` only in the generator body |
| **asyncio coroutines** | No (stackless) | `await` only, coloring propagates |
| **greenlet** | **Yes (stackful)** | The stackful primitive under gevent |
| **Stackless Python** | Yes | A historical CPython fork with built-in fibers ("tasklets") |

**greenlet** (which powers [gevent](green-threads.md)) is Python's practical stackful-coroutine library — a greenlet can switch from anywhere in its call stack, exactly the fiber property. Stackless Python was a whole alternative interpreter built around this idea.

---

## Why it matters

The stackful/stackless distinction explains a lot of real Python design:

- It's *why* asyncio needs `async`/`await` everywhere (stackless coroutines can't suspend implicitly) — the "colored functions" that some find annoying.
- It's *why* gevent (stackful, via greenlet) can make ordinary synchronous code concurrent by monkey-patching — no coloring needed.
- Neither is strictly better: stackful is more transparent, stackless is more explicit (you can *see* every suspension point).

!!! tip "You'll rarely use fibers directly"
    Day to day you'll use asyncio (stackless) or maybe gevent (stackful via greenlet), not raw fibers. But understanding stackful vs stackless is what makes the tradeoffs of `async`/`await` — and why it "colors" your functions — finally make sense.

---

## Practice exercises

1. Try to make the `fiber` generator yield from inside a helper function it calls — observe why it can't (stackless limit).
2. Research greenlet and write (or read) an example that switches from inside a nested call (stackful).
3. Explain the "function color" problem using the stackless model.
4. Compare how a fiber and an asyncio coroutine each handle suspending deep in a call chain.
5. Explain why gevent doesn't need `async`/`await` but asyncio does, in terms of stacks.
