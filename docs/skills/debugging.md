---
title: Debugging Strategies
description: Systematic debugging, scientific method, rubber duck and common bug patterns
---

# Debugging Strategies <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🧠 Soft Skills · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
  </div>
</div>

---

## The scientific method for debugging

```
1. OBSERVE   — What exactly is the symptom?
2. HYPOTHESIZE — What could cause this?
3. PREDICT   — If my hypothesis is right, what should happen when I...?
4. EXPERIMENT — Test the prediction
5. CONCLUDE  — Was I right? If not, new hypothesis.
```

---

## Strategy ladder (try in order)

| Step | Method | When |
|---|---|---|
| 1 | **Read the error message** | Always start here — Python errors are clear |
| 2 | **Reproduce minimally** | Strip away everything unrelated |
| 3 | **Add print/logging** | Quick check of values at key points |
| 4 | **Use breakpoint()** | Step through execution |
| 5 | **Binary search** | Comment out half the code — which half breaks? |
| 6 | **Rubber duck** | Explain the problem aloud (or to a duck) |
| 7 | **Git bisect** | Find which commit introduced the bug |
| 8 | **Sleep on it** | Fresh eyes see things tired eyes miss |

---

## Common Python bug patterns

```python
# 1. Mutable default argument (classic trap)
def append_to(element, target=[]):   # BAD — shared list!
    target.append(element)
    return target

# Fix:
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target

# 2. Late binding in closures
functions = [lambda x: x + i for i in range(5)]
print([f(0) for f in functions])   # [4, 4, 4, 4, 4] — all use i=4!

# Fix: capture i as default argument
functions = [lambda x, i=i: x + i for i in range(5)]
print([f(0) for f in functions])   # [0, 1, 2, 3, 4]

# 3. Modifying list while iterating
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)   # SKIPS elements!

# Fix: iterate over a copy or use comprehension
items = [x for x in items if x % 2 != 0]

# 4. == vs is
a = 1000
b = 1000
print(a == b)    # True (same value)
print(a is b)    # False! (different objects — outside cache range)

# 5. Forgetting to await
async def get_data():
    return await fetch("...")   # without await: returns coroutine, not data!
```

---

## Git bisect — find the breaking commit

```bash
git bisect start
git bisect bad                  # current commit is broken
git bisect good abc1234         # this older commit was working
# Git checks out middle commit
# You test: does the bug exist?
git bisect good   # or git bisect bad
# Repeat until: "abc5678 is the first bad commit"
git bisect reset
```

---

## Practice Exercises

1. **Debug a provided broken function** using only `print` statements (no debugger).
2. **Use `breakpoint()`** to step through a recursive function and understand state at each level.
3. **Find the bug** in 5 tricky code snippets (mutable defaults, closures, off-by-one, etc.).
4. **Use `git bisect`** to find which commit broke a test.
5. **Write a bug report** for an open-source project — include reproduction steps, expected/actual behavior.
