---
title: "Data Visualization"
description: Choosing the right chart and telling stories with data
---

# Data Visualization <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="matplotlib.md">Matplotlib</a>, <a href="seaborn.md">Seaborn</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why visualization matters
- [x] Choosing the right chart
- [x] Common mistakes to avoid
- [x] Interactive vs static
- [x] Telling a story with data

Visualization turns numbers into insight. Where [Matplotlib](matplotlib.md) and [Seaborn](seaborn.md) are the *tools*, this page is about the *craft* — picking the right chart and communicating clearly.

!!! note "Concept-focused page"
    This is about visualization principles, not library syntax (covered in Matplotlib/Seaborn and [Scientific Visualization](../../scientific/scientific-visualization.md)). The tools aren't installed here; the value here is the decision-making.

---

## Why it matters

Anscombe's quartet is the classic proof: four datasets with *identical* means, variances, and correlations look utterly different when plotted — one linear, one curved, one with an outlier. Summary statistics hid what a single glance revealed. **Always plot your data** before trusting summaries.

Visualization serves three jobs:
- **Explore** — find patterns, outliers, and structure while analyzing.
- **Explain** — communicate a finding to others.
- **Monitor** — dashboards showing live system/business state.

---

## Choosing the right chart

The chart should match the *question* and the *data type*:

| Your question | Chart |
|---|---|
| How does Y change with X (continuous)? | **Line** |
| Is there a relationship between two variables? | **Scatter** |
| How is one variable distributed? | **Histogram / KDE / box plot** |
| How do categories compare? | **Bar chart** |
| What are the parts of a whole? | **Stacked bar** (rarely pie) |
| How do two categories interact (counts)? | **Heatmap** |
| How does something change over time? | **Line / area** |

Picking wrong obscures the message — a bar chart hiding a distribution, or a pie chart with 12 slices nobody can compare.

---

## Common mistakes

!!! warning "Charts can mislead — often unintentionally"
    - **Truncated y-axis** — starting a bar chart's axis at a nonzero value exaggerates differences. Bar charts should start at zero.
    - **Pie charts with many slices** — humans can't compare angles well; a bar chart is almost always clearer.
    - **Too much on one chart** — five overlapping lines become spaghetti. Split or simplify.
    - **Bad color choices** — the `jet` colormap distorts perception; use perceptually-uniform ones like `viridis`. And ensure colorblind-safe palettes.
    - **3D when 2D would do** — 3D bar/pie charts distort proportions for no benefit.
    - **No labels** — unlabeled axes/units make a chart useless.

---

## Static vs interactive

- **Static** (Matplotlib, Seaborn) — for reports, papers, print, and anywhere a fixed image is right. Precise control.
- **Interactive** (Plotly, Bokeh, Altair) — zoom, hover, filter; great for exploration and web dashboards where users want to dig in.

```python
import plotly.express as px    # pip install plotly
fig = px.scatter(df, x="gdp", y="life_expectancy",
                 size="population", color="continent", hover_name="country")
fig.show()                     # interactive: hover, zoom, pan
```

!!! note "Plotly follows documented API"
    Not installed here. Interactive libraries shine for dashboards and exploration; static libraries for fixed publication-quality figures. Match the medium to the audience.

---

## Telling a story with data

Beyond correctness, effective visualization *communicates*:

- **One chart, one message.** Decide the single point the chart should make, and strip everything that doesn't serve it.
- **Guide the eye.** Use color/annotation to highlight the key data point, not decorate everything.
- **Order meaningfully.** Sort bars by value, not alphabetically, when the ranking is the point.
- **Add context.** A reference line, target, or annotation turns a chart from "here's data" into "here's what it means."
- **Title with the takeaway.** "Sales grew 40% after launch" beats "Monthly sales".

!!! tip "Design for your audience"
    An exploratory chart for yourself can be quick and dense. A chart for stakeholders should make its point in seconds, with the conclusion obvious. Know which you're making — the same data, different presentation.

---

## Practice exercises

1. For five questions (trend over time, category comparison, distribution, correlation, part-to-whole), name the best chart.
2. Explain how a truncated y-axis can mislead, with a concrete before/after.
3. Take a "bad" chart idea (12-slice pie) and describe a clearer alternative.
4. Rewrite a generic chart title into a takeaway-driven one for a made-up finding.
5. Decide static vs interactive for: a printed report, a live ops dashboard, an exploratory analysis — and justify each.
