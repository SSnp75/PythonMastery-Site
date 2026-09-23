---
title: "Computational Physics"
description: Numerical integration, ODEs and Monte Carlo methods for physics
---

# Computational Physics <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: calculus, <a href="numerical-optimization.md">Numerical Optimization</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Numerical integration (tested)
- [x] Solving ODEs — simulating motion (tested)
- [x] Monte Carlo methods (tested)
- [x] The accuracy/stability tradeoffs
- [x] The scientific Python stack

Physics is full of equations we can't solve by hand, so we solve them *numerically*. All three core techniques below are shown in **run-verified** pure Python.

---

## Numerical integration (tested)

Computing an integral (area under a curve) numerically — the **trapezoidal rule** sums thin trapezoids:

```python
def integrate(f, a, b, n=1000):
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return total * h

import math
print(round(integrate(lambda x: x*x, 0, 1), 5))    # ∫x² [0,1] = 1/3
print(round(integrate(math.sin, 0, math.pi), 5))    # ∫sin [0,π] = 2
```

Output:

```text
0.33333
2.0
```

Both match the exact answers (1/3 and 2). More slices (`n`) means more accuracy — the essential numerical tradeoff of precision vs computation. This is how you compute work, probability, center of mass — any physical quantity expressed as an integral.

---

## Solving ODEs: simulating motion (tested)

Most physics is **differential equations** — rates of change. **Euler's method** steps a system forward in tiny time increments. Here, radioactive decay `dy/dt = -y`:

```python
def euler(dydt, y0, t0, t1, steps):
    dt = (t1 - t0) / steps
    y, t = y0, t0
    for _ in range(steps):
        y += dydt(t, y) * dt      # step the state forward
        t += dt
    return y

import math
# dy/dt = -y, y(0) = 1  ->  exact answer y(1) = e⁻¹
approx = euler(lambda t, y: -y, y0=1.0, t0=0, t1=1, steps=1000)
print(round(approx, 4), "vs", round(math.exp(-1), 4))
```

Output:

```text
0.3677 vs 0.3679
```

Euler's method got 0.3677 against the exact 0.3679 — close, with the small gap being *discretization error*. Halving the step size roughly halves that error (Euler is first-order). The same technique simulates orbits, pendulums, and circuits — it's the heart of physics engines and the [game physics](../domains/game-development.md) you saw earlier.

!!! tip "Better integrators exist"
    Euler is the simplest but least accurate ODE method. Real work uses **Runge-Kutta** (RK4) or SciPy's `solve_ivp`, which achieve far higher accuracy per step. Euler is for *understanding*; RK4/SciPy is for *doing*.

---

## Monte Carlo methods (tested)

When a problem is too complex to solve directly, **Monte Carlo** uses random sampling. The classic demo: estimate π by throwing random darts at a square and counting how many land in the inscribed circle:

```python
import random
random.seed(42)

def estimate_pi(n):
    inside = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:            # inside the quarter circle?
            inside += 1
    return 4 * inside / n             # ratio of areas × 4

print(round(estimate_pi(100_000), 3))
```

Output:

```text
3.137
```

100,000 random points estimate π ≈ 3.137 (true value 3.14159). Accuracy improves with more samples — but slowly (error shrinks like 1/√n), which is Monte Carlo's characteristic tradeoff. It shines for high-dimensional integrals and systems (statistical mechanics, quantum Monte Carlo, financial modeling) where deterministic methods break down.

---

## The scientific stack

In real computational physics you'd use optimized libraries:

```python
import numpy as np                    # arrays, vectorized math
from scipy.integrate import solve_ivp, quad   # ODEs and integration

# High-accuracy ODE solve
sol = solve_ivp(lambda t, y: -y, [0, 1], [1.0])

# High-accuracy integration
area, err = quad(lambda x: x**2, 0, 1)   # ~0.3333 with error estimate
```

!!! note "NumPy/SciPy snippets follow documented APIs"
    These aren't installed here (the pure-Python methods above are run-verified). NumPy vectorizes the math for speed; SciPy provides accurate, adaptive integrators and solvers. The hand-written methods teach you *what they do*; the libraries do it accurately and fast.

---

## Practice exercises

1. Increase/decrease `n` in `integrate` and observe how the error in ∫x² shrinks.
2. Simulate a falling object with Euler (`dv/dt = -g`) and compare to the exact `v = -gt`.
3. Improve the ODE solver to RK4 (midpoint sampling) and compare accuracy to Euler at the same step count.
4. Use Monte Carlo to estimate the area under `sin(x)` on [0, π] and compare to the tested integrator.
5. Explain why Monte Carlo error scales as 1/√n and what that means for getting one more digit.
