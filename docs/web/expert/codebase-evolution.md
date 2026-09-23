---
title: "Long-term Codebase Evolution"
description: Refactoring strategies, deprecation policies and architectural change over years
---

# Long-term Codebase Evolution <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="clean-architecture/">Clean Architecture</a>, <a href="../../testing/pytest/">Testing</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Refactor safely behind a test net
- [x] Deprecate APIs gracefully with warnings
- [x] Migrate away from old code with the strangler pattern
- [x] Manage architectural change over years
- [x] Keep documentation and decisions traceable

---

## The reality

Code that lives for years faces a force nothing else does: **continuous change under continuous use**. Requirements shift, the team turns over, dependencies age out, and the "temporary" hack from 2021 is now load-bearing. Evolving such a codebase isn't about grand rewrites — those usually fail. It's about a set of disciplined, incremental practices that let a system change shape while staying alive.

---

## Refactoring safely

Refactoring means changing *structure* without changing *behavior*. The only thing that makes it safe is a **test net** — tests that fail if behavior changes.

The loop:

```
1. Ensure tests cover the code you're about to change (add them if not).
2. Make one small structural change.
3. Run the tests — they must still pass (behavior unchanged).
4. Commit.
5. Repeat.
```

!!! tip "Characterization tests before touching legacy code"
    When code has no tests and you don't fully understand it, first write **characterization tests** — tests that capture what it *currently* does (even quirks). They're not judging whether the behavior is right; they pin it down so your refactor can't silently change it. Only then start restructuring.

Keep refactoring commits **separate** from behavior-changing commits. A reviewer can trust a "pure refactor" PR quickly; mixing the two hides real changes among noise.

---

## Deprecation: retiring an API gracefully

You rarely delete a public function outright — callers depend on it. Instead you **deprecate**: keep it working, but warn users to move on, then remove it in a later release.

Python's `warnings` module is the standard mechanism. Runnable:

```python
import warnings

def old_api(x):
    warnings.warn(
        "old_api() is deprecated; use new_api() instead",
        DeprecationWarning,
        stacklevel=2,          # point the warning at the CALLER, not here
    )
    return new_api(x)          # keep working by delegating

def new_api(x):
    return x * 2
```

Calling `old_api(21)` still returns the right answer and raises a `DeprecationWarning`:

```python
import warnings
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    result = old_api(21)
    print("result:  ", result)
    print("warning: ", caught[0].message)
    print("category:", caught[0].category.__name__)
```

Output:

```text
result:   42
warning:  old_api() is deprecated; use new_api() instead
category: DeprecationWarning
```

The old call keeps working (returns `42`) while telling the caller exactly what to switch to. `stacklevel=2` makes the warning point at the line that *called* `old_api`, not the line inside it — so users see where in *their* code the fix belongs.

**A humane deprecation policy:**

1. **Announce** — deprecate in a release, with a warning naming the replacement and a removal timeline.
2. **Overlap** — keep old and new working together for a stated period (a version, a quarter — long enough for users to migrate).
3. **Remove** — delete the old path in the announced release, and say so in the changelog.

!!! note "`DeprecationWarning` is hidden by default"
    Python silences `DeprecationWarning` for end users (to avoid noise) but shows it in tests and when running with `-W`. That's intentional: library *authors* and *testers* see it, ordinary users aren't spammed. Document deprecations in your changelog too — don't rely on the warning alone.

---

## Migrating with the strangler pattern

To replace a large old subsystem without a risky big-bang rewrite, use the **strangler fig** pattern (named after the vine that grows around a tree and gradually replaces it):

```
Route new work to the new implementation, piece by piece, until the old one is dead:

  [ all traffic ] → OLD system
  [ 90% ]→ OLD     [ 10% ]→ NEW      ← start small
  [ 50% ]→ OLD     [ 50% ]→ NEW
  [  0% ]→ OLD     [100% ]→ NEW      ← old system now dead code → delete
```

You put a routing layer (a facade, a feature flag, an API gateway) in front, and migrate one capability at a time. Each step is small, reversible, and shippable. The old system keeps running until the last piece is moved — then you delete it. This is how you replace a monolith or a legacy module without a months-long freeze.

Feature flags (see [Hot-swappable Components](hot-swappable-components.md)) are the usual routing mechanism, letting you shift traffic gradually and roll back instantly if the new path misbehaves.

---

## Managing architectural change

Big structural shifts (new persistence layer, splitting a monolith, changing frameworks) need more than code discipline:

- **Record decisions with ADRs.** An *Architecture Decision Record* is a short document capturing *what* was decided, *why*, and *what alternatives* were rejected. Years later, ADRs answer "why on earth is it built this way?" — preventing the team from re-litigating settled choices or, worse, undoing a decision without knowing its rationale.
- **Prefer incremental over big-bang.** The graveyard of software is full of "we'll rewrite it properly" projects that never shipped. Evolve in place with the strangler pattern.
- **Fight entropy continuously.** Small, ongoing cleanup (the "boy scout rule" — leave code a little better than you found it) beats periodic heroic refactors.
- **Keep dependencies current.** Upgrading regularly is annoying; upgrading after five years of neglect is a project. Automate dependency updates and run them often.

---

## Documentation that survives

Code outlives memory. What keeps a long-lived codebase maintainable:

- **A changelog** — every notable change, especially deprecations and breaking changes, so users and future maintainers can trace what happened and when.
- **ADRs** — the *why* behind structural choices.
- **READMEs close to the code** — how to build, test, and run each component, kept next to it so they're updated together.
- **Deprecation notices in the changelog**, not just as runtime warnings.

!!! tip "Write for the maintainer who has forgotten everything — because it might be you"
    In two years, nobody (including the author) will remember why a workaround exists. A one-line comment or ADR explaining a non-obvious decision saves hours of archaeology and prevents someone from "fixing" something that was deliberate.

---

## Practice exercises

1. Add a deprecation warning to a function, using `stacklevel=2`, and write a test that asserts the `DeprecationWarning` is raised (see the Testing topic for `pytest.warns`).
2. Write a characterization test for a piece of code you don't fully understand — capture its current output for several inputs.
3. Sketch a strangler-pattern migration for replacing a legacy "reports" module: what routes first, how you'd flag it, how you'd roll back.
4. Write an ADR for a real decision in one of your projects: context, decision, alternatives considered, consequences.
5. Explain why an incremental strangler migration usually beats a full rewrite, with reference to risk and shippability.
