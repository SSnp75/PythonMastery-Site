---
title: "Seaborn"
description: Statistical data visualization built on Matplotlib
---

# Seaborn <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="matplotlib.md">Matplotlib</a>, <a href="pandas.md">Pandas</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What Seaborn adds over Matplotlib
- [x] Statistical plots in one line
- [x] The main plot categories
- [x] Working with DataFrames
- [x] When to use Seaborn vs Matplotlib

**Seaborn** is a statistical visualization library built on top of [Matplotlib](matplotlib.md). It makes attractive, informative statistical graphics with far less code — and understands Pandas DataFrames directly.

!!! note "Plotting libraries need install + a display"
    Seaborn (and Matplotlib) aren't installed in this environment and produce images, so this page follows their documented APIs rather than being run-verified. The [Scientific Visualization](../../scientific/scientific-visualization.md) page covers general plotting principles.

---

## What Seaborn adds

Matplotlib is powerful but low-level — a statistical plot can take many lines. Seaborn wraps common statistical visualizations into single calls, adds attractive defaults, and speaks DataFrames:

```python
import seaborn as sns          # pip install seaborn
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")            # a built-in example DataFrame

# A scatter plot with a regression line — one call
sns.regplot(data=tips, x="total_bill", y="tip")
plt.show()
```

The same plot in raw Matplotlib would need manual regression fitting and styling. Seaborn does it in a line, and it looks good by default.

---

## The main plot categories

Seaborn organizes plots by what they show:

| Category | Plots | Shows |
|---|---|---|
| **Relational** | `scatterplot`, `lineplot` | Relationship between two variables |
| **Distribution** | `histplot`, `kdeplot`, `boxplot`, `violinplot` | How one variable is distributed |
| **Categorical** | `barplot`, `countplot`, `boxplot`, `stripplot` | Comparison across categories |
| **Matrix** | `heatmap`, `clustermap` | 2D data, correlations |
| **Multi-plot** | `pairplot`, `FacetGrid` | Many relationships at once |

```python
sns.histplot(data=tips, x="total_bill", kde=True)   # distribution + density curve
sns.boxplot(data=tips, x="day", y="total_bill")      # distribution per category
sns.heatmap(tips.corr(numeric_only=True), annot=True)  # correlation matrix
```

---

## The killer features

Two Seaborn capabilities are especially powerful:

**`pairplot`** — plot every pair of numeric columns at once, instantly revealing relationships across a whole dataset:

```python
sns.pairplot(tips, hue="time")   # scatter matrix, colored by a category
```

**Semantic mapping with `hue`/`size`/`style`** — encode extra dimensions by color, size, or marker, so one plot shows three or four variables:

```python
sns.scatterplot(data=tips, x="total_bill", y="tip",
                hue="day", size="size", style="smoker")
```

These turn exploratory data analysis into a few expressive lines — a big reason Seaborn is a staple of data science notebooks.

---

## Seaborn vs Matplotlib

They're complementary, not competitors (Seaborn *is* Matplotlib underneath):

- **Seaborn** — for statistical plots, quick exploration, attractive defaults, DataFrame-native work. Reach for it first in data analysis.
- **Matplotlib** — for fine-grained control, custom/non-statistical plots, and final polish. You often start with Seaborn and tweak with Matplotlib (`plt.` calls work on Seaborn plots).

!!! tip "Explore with Seaborn, polish with Matplotlib"
    In a typical workflow: use Seaborn to rapidly explore and understand your data (pairplot, distributions, correlations), then drop to Matplotlib for the exact styling when preparing a final figure. Since Seaborn returns Matplotlib axes, you get both.

---

## Practice exercises

1. Describe which Seaborn plot you'd use to see the distribution of a single numeric column.
2. Explain what `hue="category"` adds to a scatter plot and why it's useful.
3. When would you use a `boxplot` vs a `violinplot` for showing distributions per category?
4. Describe what a `heatmap` of a correlation matrix reveals at a glance.
5. Explain the division of labor between Seaborn and Matplotlib in a real analysis workflow.
