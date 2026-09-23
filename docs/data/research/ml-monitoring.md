---
title: "ML Monitoring"
description: Detect drift, track performance and keep production models healthy
---

# ML Monitoring <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="ml-deployment.md">ML Deployment</a>, <a href="../../embedded/system-monitoring.md">System Monitoring</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why models degrade in production
- [x] Detect data drift (tested)
- [x] Track model performance
- [x] Data-quality monitoring
- [x] The feedback loop

Unlike ordinary software, an ML model can **silently get worse** without any code changing — because the world it was trained on shifts. ML monitoring catches this. The drift-detection logic here is **run-verified**.

---

## Why models degrade

A deployed model was trained on *past* data. As reality drifts away from that data, predictions get worse — without any error or crash. This is unique to ML: the code is fine, but the *world* changed.

- **Data drift** — the input distribution shifts (e.g. new user demographics, seasonal change).
- **Concept drift** — the relationship between inputs and outputs changes (e.g. spam tactics evolve, so old patterns stop predicting spam).
- **Data-quality issues** — an upstream pipeline breaks, feeding garbage or nulls.

Monitoring makes these *visible* so you can retrain or fix before damage accumulates.

---

## Detecting data drift (tested)

Compare the distribution of live data against the training baseline. A standard approach buckets both and measures how much the proportions differ (a PSI-style metric). Runnable:

```python
import math

def bucketize(values, edges):
    counts = [0] * (len(edges) + 1)
    for v in values:
        for i, e in enumerate(edges):
            if v <= e:
                counts[i] += 1
                break
        else:
            counts[-1] += 1
    total = len(values)
    return [c / total for c in counts]

def population_drift(reference, current, edges):
    p, q = bucketize(reference, edges), bucketize(current, edges)
    psi = 0.0
    for pi, qi in zip(p, q):
        if pi > 0 and qi > 0:
            psi += (qi - pi) * math.log(qi / pi)
    return psi

edges = [0, 10, 20]
reference = [5, 5, 15, 25, 5, 15]          # training-time distribution
similar   = [5, 6, 15, 24, 4, 16]          # live data, still similar
shifted   = [25, 26, 27, 28, 29, 30]       # live data, drifted

print(f"drift (similar): {population_drift(reference, similar, edges):.3f}")
print(f"drift (shifted): {population_drift(reference, shifted, edges):.3f}")
```

Output:

```text
drift (similar): 0.000
drift (shifted): 1.493
```

Data similar to the baseline scores ~0 (no drift); data that shifted into different buckets scores high (1.493). A threshold on this metric (a common rule of thumb: PSI > 0.2 warrants attention) triggers an alert or retraining. This is exactly how production drift monitors work — bucket the reference, bucket the live data, measure divergence.

---

## Tracking performance

Where you have ground-truth labels (eventually), track accuracy/precision/recall/etc. over time and alert on drops. The challenge: **labels are often delayed** (you learn if a loan defaulted months later). So monitoring combines:

- **Leading indicators** — drift metrics (above), prediction distribution shifts — available *immediately*.
- **Lagging indicators** — actual accuracy once labels arrive — the ground truth, but delayed.

Drift monitoring is valuable precisely because it warns you *before* the accuracy numbers confirm the damage.

---

## Data-quality monitoring

Often the problem isn't the model — it's broken input. Monitor for:

- Nulls/missing values spiking.
- Values out of expected range or type.
- Schema changes (a column disappears/renames).
- Volume anomalies (10× more or fewer records than usual).

This overlaps with [Data Cleaning](../intermediate/data-cleaning.md) validation — the same checks, run continuously in production.

---

## Tools & the feedback loop

Python ML-monitoring tools (documented; not installed here): **Evidently**, **whylogs/WhyLabs**, **NannyML**, **Arize**. They compute drift, performance, and data-quality metrics and dashboard/alert on them.

```python
# Evidently-style workflow (documented API)
# 1. Log a reference dataset (training distribution)
# 2. Continuously log production inputs + predictions
# 3. Compute drift/quality reports on a schedule
# 4. Alert when metrics cross thresholds  -> investigate / retrain
```

!!! tip "Close the loop"
    Monitoring is only useful if it drives action. The mature setup is a **feedback loop**: monitor → detect drift/degradation → collect fresh labeled data → retrain → redeploy → monitor. Combine with general [System Monitoring](../../embedded/system-monitoring.md) (latency, errors) — an ML service needs *both* ML metrics and ordinary ops metrics.

!!! note "Tools follow documented APIs"
    The monitoring libraries aren't installed here (the drift metric above is run-verified). They productionize exactly this kind of distribution comparison at scale, with dashboards and alerting.

---

## Practice exercises

1. Add a threshold to `population_drift` that returns "drift detected" when PSI > 0.2.
2. Monitor a *categorical* feature's drift by comparing category proportions instead of numeric buckets.
3. Track prediction-distribution drift (the model's *outputs*), not just inputs — and explain why that helps when labels are delayed.
4. Write a data-quality check that flags when the null rate of a column exceeds a threshold.
5. Explain the difference between data drift and concept drift with a concrete example of each.
