---
title: "Actor Model"
description: Concurrency via isolated actors that communicate only by messages
---

# Actor Model <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prereqs: <a href="threading.md">Threading</a>, <a href="../../web/expert/event-driven-architecture.md">Event-driven Architecture</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What the actor model is and why it avoids shared-state bugs
- [x] Build an actor with a mailbox (tested)
- [x] How actors isolate faults
- [x] The Python actor ecosystem

The **actor model** is a concurrency approach where independent **actors** never share memory — they communicate only by sending **messages** to each other's mailboxes. Since there's no shared state, there are no data races and no locks. The example here is **run-verified**.

---

## The core idea

```
   actor A  ──message──▶  [mailbox]  actor B
                           processes one message at a time,
                           updates its OWN private state
```

Each actor:
- has **private state** nobody else can touch,
- has a **mailbox** (queue) of incoming messages,
- processes messages **one at a time**, so its own state is never accessed concurrently.

This sidesteps the hardest part of concurrency — shared mutable state (see [Threading](threading.md)). No locks, no races, because nothing is shared.

---

## An actor with a mailbox (tested)

Using a thread + a queue as the mailbox. Runnable:

```python
import queue
import threading

class Actor:
    def __init__(self):
        self.inbox = queue.Queue()          # the mailbox
        self.state = 0                       # PRIVATE state
        self._run = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def send(self, msg):                     # the only way to interact
        self.inbox.put(msg)

    def _loop(self):
        while self._run:
            msg = self.inbox.get()
            if msg == "STOP":
                self._run = False
            elif isinstance(msg, tuple) and msg[0] == "add":
                self.state += msg[1]         # safe: only this thread touches state
            self.inbox.task_done()
```

```python
a = Actor()
for i in [1, 2, 3, 4]:
    a.send(("add", i))
a.inbox.join()                # wait until all messages processed
print("actor state:", a.state)
a.send("STOP")
```

Output:

```text
actor state: 10
```

Four `add` messages sent concurrently from the main thread all landed in the mailbox and were processed **one at a time** by the actor, giving the correct total of 10 — with **no lock** around `self.state`. That's the actor guarantee: because only the actor's own loop touches its state, concurrency bugs on that state are impossible by design.

---

## Fault isolation

A key benefit: actors are isolated, so one crashing doesn't corrupt others. In mature actor systems (like Erlang/Akka), this becomes a **supervision** strategy — a supervisor actor watches its children and restarts them on failure ("let it crash"). Because state isn't shared, a failed actor can be replaced cleanly without leaving the system in a half-broken state. This is the philosophy behind highly reliable systems like telecom switches.

---

## The Python ecosystem

Python has no built-in actor system, but several options exist:

| Tool | Notes |
|---|---|
| **Threads/processes + queues** | Roll your own (as above) — fine for simple cases |
| **Pykka** | A lightweight actor library |
| **Thespian**, **Ray** | Distributed actors across machines (Ray is popular for ML) |
| **`multiprocessing`** | Process-based isolation with queues ([Multiprocessing](multiprocessing.md)) |

!!! tip "Actors vs shared-state threading"
    If you find yourself adding locks everywhere and still hitting races, the actor model is often a cleaner mental model: give each unit of concurrency its own state and a mailbox, and communicate by messages. It trades a little overhead (message passing) for a lot of correctness (no shared state). It's the same decoupling idea as an [event bus](../../web/expert/event-driven-architecture.md), applied to concurrency.

---

## Practice exercises

1. Add a `"get"` message that makes the actor put its state onto a reply queue you pass in.
2. Create two actors that send messages to each other (a ping-pong), stopping after N rounds.
3. Add a supervisor that restarts an actor if its loop raises an exception.
4. Compare the actor version to a lock-based counter — which is easier to reason about?
5. Explain why the actor needs no lock around `self.state`, referencing who touches it.
