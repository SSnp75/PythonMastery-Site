---
title: "Python for Simulation"
description: Model complex systems with agent-based and discrete-event simulation
---

# Python for Simulation <span class="pm-badge pm-badge-proficient">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../core/intermediate/iterators-generators.md">Iterators & Generators</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The main simulation styles
- [x] Build an agent-based model (tested)
- [x] Understand discrete-event simulation
- [x] The library ecosystem

Simulation lets you study systems too complex, expensive, or dangerous to experiment on directly — epidemics, traffic, markets, ecosystems. The agent-based example here is **run-verified** with pure Python.

---

## Styles of simulation

- **Agent-based** — model individual agents and their local rules; global behavior *emerges* (traffic jams, flocking, disease spread).
- **Discrete-event** — jump between timestamped events (see the tested engine in [Hardware Simulation](../embedded/hardware-simulation.md)); great for queues, logistics.
- **Continuous / numerical** — solve equations over time (physics, chemistry); needs NumPy/SciPy.

---

## Agent-based model (tested)

Conway's Game of Life is the classic agent-based model: each cell lives or dies based on its neighbors. A cell survives with 2-3 neighbors, is born with exactly 3. Runnable:

```python
def neighbors(cells, x, y):
    return sum((nx, ny) in cells
               for nx in (x-1, x, x+1) for ny in (y-1, y, y+1)
               if (nx, ny) != (x, y))

def step(cells):
    # only cells and their neighbors can change
    candidates = set()
    for (x, y) in cells:
        for nx in (x-1, x, x+1):
            for ny in (y-1, y, y+1):
                candidates.add((nx, ny))
    new = set()
    for (x, y) in candidates:
        n = neighbors(cells, x, y)
        if (x, y) in cells and n in (2, 3):
            new.add((x, y))              # survives
        elif (x, y) not in cells and n == 3:
            new.add((x, y))              # born
    return new
```

A "blinker" (3 cells in a row) oscillates:

```python
blinker = {(0, 1), (1, 1), (2, 1)}      # horizontal
print(sorted(step(blinker)))            # becomes vertical
print(step(step(blinker)) == blinker)   # back to horizontal after 2 steps
```

Output:

```text
[(1, 0), (1, 1), (1, 2)]
True
```

The horizontal blinker becomes vertical, then returns to horizontal — a period-2 oscillator. Complex behavior from three trivial rules, computed with only `set` and loops. That emergence is the whole appeal of agent-based modeling. Representing the grid as a *set of live cells* (rather than a full 2D array) keeps it efficient even on an infinite plane.

---

## Discrete-event simulation

For systems that change at discrete moments (a customer arrives, a machine finishes), **discrete-event simulation** jumps from event to event rather than ticking through time. The [Hardware Simulation](../embedded/hardware-simulation.md) page has a full, tested event-queue engine — the same technique applies to modeling a bank queue, a factory line, or a network.

For serious models, **`simpy`** provides resources, queues, and processes on top of Python generators:

```python
import simpy    # pip install simpy

def customer(env, name, teller):
    with teller.request() as req:      # wait for a free teller
        yield req
        yield env.timeout(5)           # service takes 5 time units

env = simpy.Environment()
teller = simpy.Resource(env, capacity=2)
# env.process(...) for each customer; env.run(until=...)
```

!!! note "simpy snippet follows documented API"
    `simpy` isn't installed here; this follows its documented API. The agent-based Life example above **is** run-verified.

---

## The ecosystem

| Need | Tool |
|---|---|
| Discrete-event | SimPy |
| Agent-based | Mesa |
| Numerical / ODEs | NumPy, SciPy |
| Visualization | Matplotlib, and the [Scientific Visualization](../scientific/scientific-visualization.md) topic |

---

## Practice exercises

1. Add a "glider" starting pattern to the Life model and watch it move across steps.
2. Count the live-cell population at each step and detect when it stabilizes.
3. Model a simple SIR epidemic: agents are Susceptible/Infected/Recovered with transition probabilities.
4. Rebuild a bank-queue simulation using the discrete-event engine from Hardware Simulation.
5. Explain when agent-based vs discrete-event vs continuous simulation is the right choice.
