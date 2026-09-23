---
title: "Hexagonal Architecture"
description: Ports and adapters — isolate your domain from frameworks, databases and I/O
---

# Hexagonal Architecture <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../proficient/frameworks/">Web Frameworks</a>, <a href="clean-architecture/">Clean Architecture</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The ports & adapters model and why it exists
- [x] The difference between driving and driven ports
- [x] Keep the domain free of frameworks and I/O
- [x] Swap adapters (DB, notifier) without touching business logic
- [x] Test the core with zero infrastructure

---

## The idea

Hexagonal Architecture — also called **Ports and Adapters** (Alistair Cockburn, 2005) — puts your business logic in the center and pushes everything external (web frameworks, databases, message queues, email) to the edges. The center talks to the outside world only through **ports** (interfaces), and the outside world plugs in through **adapters** (implementations).

```
            DRIVING SIDE                         DRIVEN SIDE
        (who calls the app)                 (what the app calls)

   HTTP API  ─┐                                    ┌─  SQL database
   CLI       ─┼──▶ [driving port] ─▶ DOMAIN ─▶ [driven port] ─┼─  email service
   Tests     ─┘                     (core)                    └─  message queue
```

The one rule: **dependencies point inward.** The domain knows nothing about the adapters. The adapters depend on the domain, never the reverse. That inversion is what makes the core swappable and testable.

**Two kinds of port:**

- **Driving (inbound) port** — the API the outside world uses to *drive* the application (your use case). An HTTP controller or a test calls it.
- **Driven (outbound) port** — the API the application uses to reach something external (a repository, a notifier). The application defines the interface; an adapter fulfills it.

!!! note "Hexagonal vs Clean Architecture"
    They share the same core insight (dependency inversion around a framework-free domain). Clean Architecture adds more named layers (entities, use cases, adapters, frameworks). Hexagonal is the simpler, older formulation: domain in the middle, ports around it, adapters outside. Learn hexagonal first; Clean is an elaboration.

---

## Worked example: money transfer

We'll build a `TransferMoney` use case with **pure Python — no framework needed** so every line here is runnable and the outputs are real.

### The domain core

The center holds entities and business rules. It imports nothing external.

```python
from dataclasses import dataclass

class InsufficientFundsError(Exception):
    pass

@dataclass
class Account:
    id: str
    balance: float = 0.0

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"balance {self.balance} < requested {amount}"
            )
        self.balance -= amount

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
```

The rule "you can't withdraw more than your balance" lives **inside the entity**, not in a controller or a database trigger. That's the point — business rules belong in the core.

### The ports (interfaces)

The application declares what it *needs* from the outside, using `Protocol` (structural typing — an adapter matches just by having the right methods, no inheritance required).

```python
from typing import Protocol

class AccountRepository(Protocol):     # driven port
    def get(self, account_id: str) -> Account | None: ...
    def save(self, account: Account) -> None: ...

class Notifier(Protocol):              # driven port
    def notify(self, account_id: str, message: str) -> None: ...
```

Notice these describe *capabilities*, not technologies. There's no mention of SQL, Redis, or SMTP — the core doesn't care how the work gets done.

### The use case (driving port)

```python
class TransferMoney:
    def __init__(self, repo: AccountRepository, notifier: Notifier) -> None:
        self.repo = repo
        self.notifier = notifier

    def execute(self, src_id: str, dst_id: str, amount: float) -> None:
        src = self.repo.get(src_id)
        dst = self.repo.get(dst_id)
        if src is None or dst is None:
            raise LookupError("account not found")
        src.withdraw(amount)          # domain rule enforced here
        dst.deposit(amount)
        self.repo.save(src)
        self.repo.save(dst)
        self.notifier.notify(src_id, f"Sent {amount} to {dst_id}")
```

The use case orchestrates the flow but delegates *how* things are stored and *how* users are notified to whatever adapters get injected. It depends only on the port interfaces.

### The adapters

Now we provide concrete implementations. Here's an in-memory repository and two notifiers (a real one and a test one):

```python
class InMemoryAccountRepository:       # adapter for AccountRepository
    def __init__(self) -> None:
        self._store: dict[str, Account] = {}
    def get(self, account_id: str) -> Account | None:
        return self._store.get(account_id)
    def save(self, account: Account) -> None:
        self._store[account.id] = account

class ConsoleNotifier:                 # adapter for Notifier
    def notify(self, account_id: str, message: str) -> None:
        print(f"[notify {account_id}] {message}")

class FakeNotifier:                    # test adapter
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []
    def notify(self, account_id: str, message: str) -> None:
        self.messages.append((account_id, message))
```

In a real app the repository adapter would use SQLAlchemy and the notifier would send email — but the use case wouldn't change one character.

### Wiring and running it

```python
repo = InMemoryAccountRepository()
repo.save(Account("alice", 100.0))
repo.save(Account("bob", 0.0))

TransferMoney(repo, ConsoleNotifier()).execute("alice", "bob", 30.0)

print(repo.get("alice").balance)
print(repo.get("bob").balance)
```

Output:

```text
[notify alice] Sent 30.0 to bob
70.0
30.0
```

---

## Testability — the payoff

Because the core depends only on ports, tests inject fakes and run with **no database, no network, no framework** — instantly.

```python
def test_transfer_moves_money_and_notifies():
    repo = InMemoryAccountRepository()
    repo.save(Account("alice", 100.0))
    repo.save(Account("bob", 0.0))
    notifier = FakeNotifier()

    TransferMoney(repo, notifier).execute("alice", "bob", 30.0)

    assert repo.get("alice").balance == 70.0
    assert repo.get("bob").balance == 30.0
    assert notifier.messages == [("alice", "Sent 30.0 to bob")]

def test_transfer_rejects_overdraft():
    repo = InMemoryAccountRepository()
    repo.save(Account("alice", 10.0))
    repo.save(Account("bob", 0.0))

    try:
        TransferMoney(repo, FakeNotifier()).execute("alice", "bob", 50.0)
        assert False, "should have raised"
    except InsufficientFundsError as e:
        assert str(e) == "balance 10.0 < requested 50.0"
```

Both tests pass. The overdraft test confirms the domain rule fires and produces the message `balance 10.0 < requested 50.0` — exercised without any infrastructure.

---

## Swapping adapters (plugin-like integrations)

The same use case works with a different notifier, chosen at wiring time:

```python
import os

# Pick the adapter based on environment — the core is untouched
notifier = ConsoleNotifier() if os.environ.get("ENV") == "dev" else FakeNotifier()
TransferMoney(repo, notifier).execute("alice", "bob", 5.0)
```

This is why hexagonal design scales: adding "send an SMS instead of email" means writing one new adapter class that satisfies the `Notifier` port. No use case, entity, or test of the core needs to change.

---

## When to use it (and when not)

**Use it when:**

- The domain logic is rich and worth protecting from churn in frameworks/DBs.
- You expect to swap infrastructure (change DB, add a new delivery channel).
- Testability and long life matter more than raw line-count.

**Skip it when:**

- The app is a thin CRUD wrapper over a database — the ceremony outweighs the benefit.
- It's a short-lived script or prototype.

!!! warning "Don't over-abstract"
    A port with exactly one adapter that will never change is just indirection. Introduce a port when you have a real reason to vary the implementation (testing counts as a reason; "maybe someday" usually doesn't).

---

## Practice exercises

1. Add a `PostgresAccountRepository` adapter (real or sketched) that satisfies the same `AccountRepository` port, and confirm `TransferMoney` needs no changes.
2. Add an `AuditLog` driven port and an adapter that records every transfer; inject a fake in tests to assert the audit entry.
3. Add a driving adapter: a tiny CLI (`argparse`) that reads `src dst amount` and calls `TransferMoney`.
4. Write a test that swaps in a repository which raises on `save`, and assert the use case surfaces the error sensibly.
5. Explain in your notes which ports are *driving* and which are *driven* in this example, and why the distinction matters.
