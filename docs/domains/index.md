---
title: "Domain Applications"
description: Python across industries — finance, science, geospatial, games, IoT, robotics and more
---

# 🌍 Domain Applications

**Python is a lingua franca across wildly different fields. This section shows how it's applied in specific domains — and the libraries each one lives on.**

The core language is the same everywhere; what changes is the ecosystem of domain libraries and the problems you solve. Seeing a few domains helps you recognize which of your skills transfer and what specialized tools each field expects.

## Domains

<ul class="pm-subtopics" markdown="1">
- [💰 Python for Finance](finance.md) — time series, risk, backtesting
- [🧬 Python for Bioinformatics](bioinformatics.md) — sequences, genomics, BioPython
- [🗺️ Python for GIS](gis.md) — geospatial data, mapping, GeoPandas
- [🎲 Python for Simulation](simulation.md) — agent-based and discrete-event models
- [🎮 Python for Game Development](game-development.md) — Pygame, game loops
- [📡 Python for IoT](iot.md) — sensors, MQTT, edge devices
- [🤖 Python for Robotics](robotics.md) — control, sensing, ROS
- [⚛️ Python for Quantum Research](quantum-research.md) — qubits, circuits, Qiskit
</ul>

---

## A note on honesty

!!! note "Many domain libraries aren't installed in this build"
    Domains like data science, bioinformatics, GIS, and quantum rely on heavy third-party libraries (NumPy, Pandas, BioPython, GeoPandas, Qiskit) not present in this documentation environment. Where a page uses those, the code follows their **documented APIs** and is marked as such. Where a domain's core logic can be shown in **pure standard-library Python** (financial math, a simulation step, a game loop, sensor smoothing), those examples are **run-verified**. Each page is explicit about which is which.

---

## The transferable core

Whatever the domain, the same fundamentals carry you: clean code, data structures, testing, and the ability to read a library's docs and apply it. A finance quant and a robotics engineer write recognizably similar Python — they just import different things. Build the core (the rest of this site), and any domain becomes a matter of learning its specific stack.
