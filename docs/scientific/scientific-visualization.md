---
title: "Scientific Visualization"
description: Plot data and render results with Matplotlib and beyond
---

# Scientific Visualization <span class="pm-badge pm-badge-proficient">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prereqs: <a href="../data/intermediate/matplotlib.md">Matplotlib</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why visualization matters in science
- [x] The Matplotlib workflow
- [x] Choosing the right plot type
- [x] 3D and volume rendering
- [x] Interactive and domain-specific tools

A plot turns numbers into understanding. Scientific visualization is how researchers explore data, verify simulations, and communicate results. Python's ecosystem — anchored by Matplotlib — covers everything from a quick line chart to interactive 3D.

!!! note "Plotting libraries need a display + install"
    Matplotlib and friends aren't installed in this environment and produce images/windows, so this page describes their documented APIs rather than running them. The [Matplotlib](../data/intermediate/matplotlib.md) topic covers the basics; this focuses on *scientific* visualization specifically.

---

## Why it matters

Numbers alone hide patterns. A visualization reveals trends, outliers, and structure the eye catches instantly. In science specifically, plots:

- **Explore** — spot the shape of data before formal analysis.
- **Verify** — does the simulation output look physically sensible?
- **Communicate** — a figure conveys a result faster than a table.

Anscombe's quartet is the classic lesson: four datasets with *identical* summary statistics look completely different when plotted. Always plot your data.

---

## The Matplotlib workflow

Matplotlib is the foundation. The standard pattern — figure, axes, plot, label:

```python
import matplotlib.pyplot as plt   # pip install matplotlib
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)

fig, ax = plt.subplots()
ax.plot(x, np.sin(x), label="sin")
ax.plot(x, np.cos(x), label="cos")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Trig functions")
ax.legend()
fig.savefig("plot.png", dpi=150)     # or plt.show() for a window
```

The `fig, ax = plt.subplots()` pattern (explicit figure and axes objects) is the recommended modern style — clearer and more controllable than the older stateful `plt.plot()` calls.

---

## Choosing the right plot

Match the plot to the data and question:

| Data / goal | Plot type |
|---|---|
| Trend over a continuous variable | Line plot |
| Relationship between two variables | Scatter plot |
| Distribution of one variable | Histogram, KDE |
| Comparison across categories | Bar chart |
| 2D field / matrix / heatmap | `imshow`, `pcolormesh` |
| Contours of a 2D function | Contour plot |
| Uncertainty | Error bars, shaded bands |

The wrong plot obscures; the right one reveals. A common scientific mistake is a bar chart where a scatter or box plot would show the real distribution.

---

## 3D and volume rendering

For 3D data — surfaces, fields, molecular structures:

- **Matplotlib `mplot3d`** — basic 3D surfaces and scatter; fine for figures, not interactivity.
- **Mayavi / PyVista** — serious 3D scientific visualization (volumes, isosurfaces, meshes).
- **VTK** — the underlying toolkit for heavy 3D/volume rendering.

```python
from mpl_toolkits.mplot3d import Axes3D
import numpy as np, matplotlib.pyplot as plt

x = y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))     # a ripple surface

fig = plt.figure()
ax = fig.add_subplot(projection="3d")
ax.plot_surface(X, Y, Z, cmap="viridis")
```

---

## Interactive & domain-specific tools

- **Plotly / Bokeh** — interactive, web-based plots (zoom, hover, pan) — great for exploration and dashboards.
- **HoloViews** — high-level interactive viz that reduces boilerplate.
- **Seaborn** — statistical plots on top of Matplotlib (see the Data & AI section).
- **Domain-specific** — Biopython for phylogenetic trees, GeoPandas/Folium for maps ([GIS](../domains/gis.md)), specialized tools per field.

!!! tip "Make figures readable"
    Scientific figures live or die on clarity: label axes *with units*, choose a perceptually-uniform colormap (`viridis`, not `jet`), make text large enough, and don't overload one plot. A figure should stand alone — a reader shouldn't need the caption to grasp the main point.

---

## Practice exercises

1. Plot the output of the tested [ODE integrator](computational-physics.md) — the decay curve `y = e⁻ᵗ` vs your Euler approximation.
2. Visualize the tested [Monte Carlo π](computational-physics.md) — scatter the random points, coloring inside/outside the circle.
3. Make a histogram of 10,000 samples from `random.gauss` and confirm the bell shape.
4. Plot the [gradient descent](numerical-optimization.md) path descending toward the minimum.
5. Explain why `viridis` is a better default colormap than `jet` (perceptual uniformity).
