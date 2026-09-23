---
title: "Simulation Frameworks"
description: Tools for discrete-event, agent-based and continuous simulation in Python
---

# Simulation Frameworks <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prereqs: <a href="../domains/simulation.md">Python for Simulation</a>, <a href="computational-physics.md">Computational Physics</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The three simulation paradigms
- [x] When to use each
- [x] The frameworks for each style
- [x] How simulation connects to the rest of this site

This page maps the simulation *frameworks* landscape. The runnable examples of each technique live on related pages (linked below) so this stays a focused guide to *what tool for what job*.

---

## Three paradigms

Simulation splits into three approaches, each suited to different systems:

```
   DISCRETE-EVENT        AGENT-BASED           CONTINUOUS
   jump between events    many agents,          solve equations
   (queues, logistics)    local rules →         over time
                          emergent behavior     (physics, chemistry)
   → SimPy                → Mesa                 → NumPy/SciPy
```

| Paradigm | Models | Time | Example |
|---|---|---|---|
| **Discrete-event** | Systems that change at distinct moments | Jumps event→event | Bank queue, factory, network |
| **Agent-based** | Many interacting individuals | Steps or events | Traffic, epidemics, markets |
| **Continuous** | Quantities evolving smoothly | Small time steps | Orbits, fluid flow, circuits |

---

## Discrete-event simulation → SimPy

Time advances by jumping to the next scheduled event, skipping idle periods — hugely efficient for systems that are mostly waiting. You saw a **complete, tested** discrete-event engine in [Hardware Simulation](../embedded/hardware-simulation.md).

For real models, **SimPy** adds resources (limited servers/tellers), queues, and process interaction on top of Python generators. Use it for operations research: queuing systems, supply chains, service capacity planning.

---

## Agent-based simulation → Mesa

Model individual agents with simple local rules; watch complex global behavior *emerge*. You saw a **tested** agent-based model (Conway's Game of Life) in [Python for Simulation](../domains/simulation.md).

**Mesa** is Python's agent-based framework — it provides agent scheduling, spatial grids, data collection, and visualization. Use it for social science, ecology, epidemiology, and economics where the interesting behavior comes from many interacting entities.

---

## Continuous simulation → NumPy/SciPy

Systems governed by differential equations evolve continuously; you approximate them with small time steps. You saw **tested** numerical ODE integration (Euler's method) in [Computational Physics](computational-physics.md).

For real work, **SciPy's `solve_ivp`** provides accurate adaptive solvers (Runge-Kutta and more), and **NumPy** vectorizes the math. Use for physics, engineering, chemical kinetics — anything described by rates of change.

---

## Choosing a paradigm

Ask what drives change in your system:

- Change happens at **distinct events** (an arrival, a completion)? → **Discrete-event** (SimPy).
- Behavior **emerges from many individuals** following rules? → **Agent-based** (Mesa).
- Quantities change **smoothly and continuously**? → **Continuous** (SciPy).

Some systems mix paradigms (a hybrid model), but most fit one primarily.

!!! note "Frameworks aren't installed here"
    SimPy, Mesa, and SciPy aren't in this environment, so their APIs are described rather than run. The *techniques* behind each are demonstrated with run-verified pure-Python examples on the linked pages — build those to understand what the frameworks automate.

---

## The ecosystem

| Paradigm | Framework | Also |
|---|---|---|
| Discrete-event | SimPy | salabim |
| Agent-based | Mesa | AgentPy |
| Continuous / ODE | SciPy | NumPy, JAX |
| Visualization | Matplotlib | see [Scientific Visualization](scientific-visualization.md) |

---

## Practice exercises

1. Classify five systems (traffic, a chemical reaction, a call center, disease spread, a pendulum) by paradigm.
2. Extend the tested [Game of Life](../domains/simulation.md) with data collection (population per step).
3. Extend the tested [ODE integrator](computational-physics.md) to model a damped oscillator.
4. Describe a system that needs a *hybrid* of two paradigms and why.
5. Explain why discrete-event simulation is more efficient than fixed-timestep for a mostly-idle system.
