---
title: "Numerical Optimization"
description: Find minima, roots and best fits with gradient and gradient-free methods
---

# Numerical Optimization <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: calculus basics, <a href="index.md">Scientific Computing intro</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What optimization means numerically
- [x] Root-finding: bisection and Newton's method (tested)
- [x] Gradient descent (tested)
- [x] Gradient-free methods
- [x] The SciPy ecosystem

Optimization — finding the input that minimizes (or maximizes) a function — underlies curve fitting, machine learning, engineering design, and more. The methods here are shown in **run-verified** pure Python.

---

## Root-finding: bisection (tested)

Finding where `f(x) = 0` is the simplest optimization-adjacent problem. **Bisection** repeatedly halves an interval known to contain a root — slow but rock-solid. Runnable:

```python
def bisect(f, lo, hi, tol=1e-9):
    assert f(lo) * f(hi) < 0          # root must be bracketed (sign change)
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid                  # root is in the left half
        else:
            lo = mid                  # root is in the right half
    return (lo + hi) / 2

# √2 is the positive root of x² - 2 = 0
print(round(bisect(lambda x: x*x - 2, 0, 2), 6))
```

Output:

```text
1.414214
```

Bisection found √2 by narrowing the interval [0, 2] until it pinned the root. It's guaranteed to converge if you start with a sign change, which makes it a reliable fallback.

---

## Newton's method (tested, faster)

**Newton's method** uses the derivative to leap toward the root — far faster convergence when it works:

```python
def newton(f, df, x0, iters=20):
    x = x0
    for _ in range(iters):
        x = x - f(x) / df(x)          # step toward the root using the slope
    return x

# f = x² - 2, f' = 2x
print(round(newton(lambda x: x*x - 2, lambda x: 2*x, x0=1.0), 6))
```

Output:

```text
1.414214
```

Same answer, but Newton converges *quadratically* — the number of correct digits roughly doubles each step. The tradeoff: it needs the derivative and can diverge from a bad starting point, whereas bisection is slower but bulletproof.

---

## Gradient descent (tested)

To *minimize* a function, **gradient descent** steps downhill — repeatedly moving against the gradient (slope). It's the engine behind training most ML models. Runnable:

```python
def gradient_descent(grad, x0, lr=0.1, iters=100):
    x = x0
    for _ in range(iters):
        x = x - lr * grad(x)          # step downhill
    return x

# minimize f(x) = (x - 3)²  ->  minimum at x = 3;  f'(x) = 2(x - 3)
minimum = gradient_descent(lambda x: 2 * (x - 3), x0=0.0)
print(round(minimum, 4))
```

Output:

```text
3.0
```

Starting at 0, it walked downhill to the minimum at x=3. The **learning rate** (`lr`) is critical: too small and it crawls; too large and it overshoots or diverges — the same tuning challenge as in machine learning.

---

## Gradient-free methods

When you can't compute a gradient (noisy, discontinuous, or black-box functions), use gradient-free approaches:

- **Grid / random search** — sample many points, keep the best. Simple, parallel, but scales poorly with dimensions.
- **Nelder-Mead (simplex)** — a geometric search needing no derivatives; SciPy's default for many problems.
- **Evolutionary / genetic algorithms** — mimic natural selection over candidate solutions.
- **Bayesian optimization** — model the function and pick promising points; great for expensive functions (like ML hyperparameter tuning).

---

## In practice: SciPy

You'd normally use **SciPy's** battle-tested optimizers rather than hand-rolling:

```python
from scipy.optimize import minimize, brentq    # pip install scipy

# minimize a function
result = minimize(lambda x: (x[0] - 3)**2, x0=[0.0])
print(result.x)          # ~[3.0]

# find a root
root = brentq(lambda x: x*x - 2, 0, 2)   # robust root-finder
```

!!! note "SciPy snippet follows documented API"
    SciPy isn't installed here, so this isn't run-verified (the pure-Python methods above are). SciPy's optimizers handle convergence criteria, multiple dimensions, constraints, and edge cases you'd otherwise get wrong — use them for real work; implement the basics once to understand them.

---

## Practice exercises

1. Use `bisect` to find the root of `cos(x) - x` (a classic fixed point near 0.739).
2. Compare iterations: how many steps does bisection vs Newton take to reach 6 digits of √2?
3. Add a divergence guard to Newton (bail if `df(x)` is near zero).
4. Minimize `f(x) = x² + 3x + 2` with gradient descent and verify against the analytic minimum.
5. Experiment with the learning rate in gradient descent — find a value that overshoots and one that's too slow.
