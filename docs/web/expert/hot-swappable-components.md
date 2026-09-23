---
title: "Hot-swappable Components"
description: Change behavior at runtime with feature flags, strategy swaps and dynamic reloading
---

# Hot-swappable Components <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="plugin-based-architectures/">Plugin-based Architectures</a>, <a href="../../deployment/cicd/">CI/CD</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Swap a component's behavior at runtime with no restart
- [x] Toggle code paths with feature flags
- [x] Reload modules dynamically with `importlib.reload`
- [x] Do zero-downtime deploys (rolling updates)
- [x] Understand the real limits and dangers of live reloading

---

## The idea

"Hot-swappable" means changing part of a running system **without stopping it**. Three levels, from safest to riskiest:

1. **Swap an object's strategy** — replace a pluggable behavior via a reference. Trivial and safe.
2. **Feature flags** — toggle which code path runs, at runtime. Safe and widely used.
3. **Reload code (`importlib.reload`)** — replace a module's code in a live process. Powerful but full of sharp edges.

Plus the deployment-level answer — **rolling updates** — which achieves zero downtime by swapping *whole instances* rather than reloading code in place.

---

## Level 1: swap a strategy at runtime

If a component holds its behavior behind an interface, swapping it is just reassigning a reference. Runnable:

```python
class PricingStrategy:
    def price(self, base: float) -> float: ...

class StandardPricing(PricingStrategy):
    def price(self, base: float) -> float:
        return base

class BlackFridayPricing(PricingStrategy):
    def price(self, base: float) -> float:
        return round(base * 0.7, 2)

class Checkout:
    def __init__(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy
    def set_strategy(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy          # hot swap — no restart
    def total(self, base: float) -> float:
        return self._strategy.price(base)
```

```python
cart = Checkout(StandardPricing())
print("before swap:", cart.total(100.0))
cart.set_strategy(BlackFridayPricing())    # flip behavior live
print("after swap: ", cart.total(100.0))
```

Output:

```text
before swap: 100.0
after swap:  70.0
```

The running `Checkout` object changed its pricing behavior mid-flight. No process restart, no re-import — just a new strategy object. This is the safest form of hot-swapping and the one to prefer: build components around interfaces (see [Plugin-based Architectures](plugin-based-architectures.md)) and swapping becomes trivial.

---

## Level 2: feature flags

A feature flag is a runtime switch that selects which code path executes. It decouples **deploying** code from **releasing** it — you ship the new path dark, then flip it on when ready.

```python
flags = {"new_checkout": False}

def checkout_flow() -> str:
    if flags["new_checkout"]:
        return "NEW checkout flow"
    return "OLD checkout flow"

print(checkout_flow())
flags["new_checkout"] = True               # flip at runtime
print(checkout_flow())
```

Output:

```text
OLD checkout flow
NEW checkout flow
```

In production the flag values come from a config service or a flag platform (LaunchDarkly, Unleash, or a simple database table), refreshed periodically — so you flip a switch in a dashboard and running processes pick it up without deploying.

**Why teams love flags:**

- **Decouple deploy from release** — merge and deploy anytime; release when the business is ready.
- **Gradual rollout** — enable for 1% of users, then 10%, then everyone.
- **Instant kill switch** — a bad feature is turned off in seconds, no rollback deploy.
- **A/B testing** — route different users to different paths.

!!! warning "Flags are debt if you don't remove them"
    Every flag is a live branch in your code. Left forever, they accumulate into a tangle of `if flag_a and not flag_b` conditions nobody understands. Delete a flag (and the dead path) once the feature is fully rolled out. Track flags with expiry dates.

---

## Level 3: reloading code with `importlib.reload`

Python can re-execute a module's source in a running process, replacing its code:

```python
import importlib
import mymodule

importlib.reload(mymodule)   # re-runs mymodule's source, updating it in place
```

This is what powers dev-server auto-reload and interactive workflows. But for production it's a minefield:

!!! danger "`importlib.reload` does NOT do what people hope"
    - **Existing objects keep the OLD class.** Instances created before the reload still point at the previous class definition — you get a confusing mix of old and new. Only *new* instances use the reloaded code.
    - **Other modules keep old references.** If module B did `from A import thing`, reloading A does not update B's `thing` — B still holds the old one.
    - **Module-level state is re-run.** Reloading re-executes top-level code, resetting or duplicating globals, registrations, and side effects.
    - **No rollback.** If the new code has a syntax error mid-reload, you can leave the module half-updated and the process broken.

    Because of these, `importlib.reload` is great for **development** and interactive experimentation, and a poor choice for updating **production** code. For production, don't reload code in place — replace whole processes with a rolling update (below).

---

## Zero-downtime deploys: rolling updates

The production-grade way to "hot swap" code is at the **infrastructure** level, not inside the Python process. Instead of reloading a module, you start new instances running the new code and retire the old ones gradually, so the service never fully goes down.

```
Rolling update (3 instances, one at a time):

  [v1] [v1] [v1]     ← all serving v1
  [v2] [v1] [v1]     ← replace one; traffic still served by the others
  [v2] [v2] [v1]
  [v2] [v2] [v2]     ← done, zero downtime
```

- **Kubernetes** does this natively (`RollingUpdate` strategy) with readiness probes so traffic only goes to instances that are actually ready.
- **Blue-green** runs two full environments and switches traffic all at once.
- **Canary** sends a small slice of traffic to the new version first, watches metrics, then proceeds.

The application's job is to make this safe: start fast, expose a health/readiness check, and **drain gracefully** (finish in-flight requests before shutting down). See the [CI/CD](../../deployment/cicd.md) and Kubernetes topics for the mechanics.

---

## Choosing the right level

| Need | Use | Restart? |
|---|---|---|
| Swap a pluggable behavior | Strategy reassignment | No |
| Toggle / gradually release a feature | Feature flag | No |
| Update code during development | `importlib.reload` | No (dev only) |
| Update code in production | Rolling update (new instances) | Per-instance, zero downtime overall |

!!! tip "Prefer swapping data/objects over reloading code"
    Reassigning a strategy or flipping a flag changes behavior by changing *values*, which is predictable. Reloading *code* in a live process is unpredictable. When you think you need `importlib.reload` in production, you almost always want a feature flag or a rolling deploy instead.

---

## Practice exercises

1. Add a `PremiumPricing` strategy and swap between all three at runtime, printing the total after each swap.
2. Turn the flag dict into a class that reads flags from a JSON file and re-reads on demand, so you can flip a flag by editing the file.
3. Demonstrate the `importlib.reload` gotcha: create an instance, reload its module after changing a method, and show the old instance still uses the old behavior.
4. Write a graceful-shutdown handler (catch SIGTERM) that stops accepting new work but finishes in-flight tasks — the piece that makes rolling updates safe.
5. Explain to a teammate why a feature flag is safer than `importlib.reload` for turning a new feature on in production.
