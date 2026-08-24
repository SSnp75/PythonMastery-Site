---
title: Matplotlib
description: Plotting, figures, subplots, styling, annotations and publication-quality charts
---

# Matplotlib <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="numpy/">NumPy</a></span>
  </div>
</div>

---

## Two APIs: pyplot vs OO

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)

# ─── pyplot (quick plots) ────────────────────────
plt.plot(x, np.sin(x))
plt.title("Sine Wave")
plt.show()

# ─── Object-oriented (recommended for complex plots) ─
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), label="sin(x)")
ax.plot(x, np.cos(x), label="cos(x)")
ax.set_title("Trigonometric Functions")
ax.set_xlabel("x (radians)")
ax.set_ylabel("y")
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig("trig.png", dpi=150, bbox_inches="tight")
plt.show()
```

---

## Common plot types

```python
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
rng = np.random.default_rng(42)

# Line plot
x = np.linspace(0, 10, 50)
axes[0, 0].plot(x, np.sin(x), "b-", linewidth=2)
axes[0, 0].plot(x, np.cos(x), "r--", linewidth=2)
axes[0, 0].set_title("Line Plot")

# Scatter plot
axes[0, 1].scatter(rng.normal(0, 1, 100), rng.normal(0, 1, 100),
                   c=rng.uniform(0, 1, 100), cmap="viridis", alpha=0.7)
axes[0, 1].set_title("Scatter Plot")

# Bar chart
categories = ["A", "B", "C", "D", "E"]
values = [23, 45, 12, 67, 34]
axes[0, 2].bar(categories, values, color="steelblue", edgecolor="black")
axes[0, 2].set_title("Bar Chart")

# Histogram
data = rng.normal(100, 15, 1000)
axes[1, 0].hist(data, bins=30, edgecolor="black", alpha=0.7, color="coral")
axes[1, 0].axvline(data.mean(), color="red", linestyle="--", label=f"Mean: {data.mean():.1f}")
axes[1, 0].legend()
axes[1, 0].set_title("Histogram")

# Box plot
groups = [rng.normal(50, 10, 100) for _ in range(4)]
axes[1, 1].boxplot(groups, labels=["Q1", "Q2", "Q3", "Q4"])
axes[1, 1].set_title("Box Plot")

# Pie chart
sizes = [35, 25, 20, 15, 5]
axes[1, 2].pie(sizes, labels=categories, autopct="%1.0f%%", startangle=90)
axes[1, 2].set_title("Pie Chart")

plt.tight_layout()
plt.savefig("all_plots.png", dpi=150)
plt.show()
```

---

## Subplots and layouts

```python
# ─── Regular grid ─────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# ─── Shared axes ──────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
axes[0].plot(x, np.sin(x))
axes[1].plot(x, np.cos(x))

# ─── Different sizes with GridSpec ────────────────
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(2, 3, figure=fig)

ax_big = fig.add_subplot(gs[0, :])      # top row, all columns
ax_bl  = fig.add_subplot(gs[1, 0])      # bottom left
ax_bm  = fig.add_subplot(gs[1, 1])      # bottom middle
ax_br  = fig.add_subplot(gs[1, 2])      # bottom right

ax_big.set_title("Main Plot (spans full width)")
ax_bl.set_title("Detail 1")
ax_bm.set_title("Detail 2")
ax_br.set_title("Detail 3")

plt.tight_layout()
plt.show()
```

---

## Styling and customization

```python
# ─── Built-in styles ─────────────────────────────
print(plt.style.available)   # list all styles
plt.style.use("seaborn-v0_8-darkgrid")   # or 'ggplot', 'dark_background', etc.

# ─── Custom colors and styles ─────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(x, np.sin(x), color="#2E86AB", linewidth=2.5, linestyle="-",
        marker="o", markevery=10, markersize=6, label="sin(x)")
ax.plot(x, np.cos(x), color="#A23B72", linewidth=2, linestyle="--",
        label="cos(x)")

ax.set_title("Custom Styled Plot", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.legend(fontsize=11, loc="upper right", framealpha=0.9)
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.2, 1.2)
ax.grid(True, alpha=0.3, linestyle="--")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()
```

---

## Annotations and text

```python
fig, ax = plt.subplots(figsize=(8, 5))
x = np.linspace(0, 4*np.pi, 200)
y = np.sin(x) * np.exp(-x/10)
ax.plot(x, y, "b-", linewidth=2)

# Find and mark the maximum
max_idx = np.argmax(y)
ax.plot(x[max_idx], y[max_idx], "ro", markersize=10)

# Annotate with arrow
ax.annotate(
    f"Maximum: {y[max_idx]:.3f}",
    xy=(x[max_idx], y[max_idx]),           # point to annotate
    xytext=(x[max_idx] + 2, y[max_idx] + 0.2),  # text position
    fontsize=11,
    arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"),
)

# Add text
ax.text(8, 0.5, "Damped oscillation", fontsize=12, style="italic", alpha=0.7)

# Add horizontal/vertical lines
ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)
ax.axvline(x=np.pi, color="green", linestyle=":", label="x = π")

plt.show()
```

---

## Colormaps and heatmaps

```python
# Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
data = rng.normal(0, 1, (10, 10))
im = ax.imshow(data, cmap="RdBu_r", aspect="auto")
ax.set_title("Correlation Matrix")
fig.colorbar(im, ax=ax, label="Correlation")

# Contour plot
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)

fig, ax = plt.subplots()
cs = ax.contourf(X, Y, Z, levels=20, cmap="viridis")
fig.colorbar(cs)
ax.set_title("Contour Plot")
```

---

## Animations

```python
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.1, 1.1)
line, = ax.plot([], [], "b-", linewidth=2)

def init():
    line.set_data([], [])
    return line,

def animate(frame):
    x = np.linspace(0, 2*np.pi, 200)
    y = np.sin(x + frame * 0.1)
    line.set_data(x, y)
    return line,

anim = FuncAnimation(fig, animate, init_func=init, frames=100, interval=50, blit=True)
anim.save("wave.gif", writer="pillow", fps=30)
plt.show()
```

---

## Integration with Pandas

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=90),
    "revenue": np.random.randn(90).cumsum() + 50,
    "users": np.random.randint(100, 500, 90),
})

# Pandas built-in plotting (uses matplotlib)
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

df.plot(x="date", y="revenue", ax=axes[0], title="Daily Revenue")
df.plot(x="date", y="users", ax=axes[1], title="Daily Active Users", color="orange")

plt.tight_layout()
plt.show()
```

---

## Saving publication-quality figures

```python
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y)

# High-quality PNG
fig.savefig("figure.png", dpi=300, bbox_inches="tight", facecolor="white")

# Vector format (best for papers)
fig.savefig("figure.pdf", bbox_inches="tight")
fig.savefig("figure.svg", bbox_inches="tight")
```

---

## Practice Exercises

1. **Create a dashboard** with 4 subplots showing different aspects of a dataset.
2. **Recreate a famous chart** (e.g., Minard's Napoleon march) in matplotlib.
3. **Build an animated plot** showing gradient descent converging on a minimum.
4. **Style a plot** to match your favorite publication's chart style.
5. **Create a correlation heatmap** for a dataset with 10+ numeric columns.
6. **Plot confidence intervals** as shaded regions around a mean line.
