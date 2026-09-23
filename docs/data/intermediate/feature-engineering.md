---
title: "Feature Engineering"
description: Turn raw data into features that make models work
---

# Feature Engineering <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="data-cleaning.md">Data Cleaning</a>, <a href="statistics.md">Statistics</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why feature engineering matters most
- [x] Encoding categorical data (tested)
- [x] Scaling and normalization (tested)
- [x] Feature creation and selection
- [x] The scikit-learn workflow

**Feature engineering** is transforming raw data into inputs (features) that help a model learn. It's often said that *feature engineering beats algorithm choice* — good features with a simple model usually outperform poor features with a fancy one. The transforms here are **run-verified** in pure Python.

---

## Encoding categorical data (tested)

Models need numbers, but data has categories ("red", "blue"). **One-hot encoding** turns each category into its own 0/1 column, avoiding a false ordering. Runnable:

```python
def one_hot(values):
    categories = sorted(set(values))
    return [{c: (1 if v == c else 0) for c in categories} for v in values]

for row in one_hot(["red", "blue", "red"]):
    print(row)
```

Output:

```text
{'blue': 0, 'red': 1}
{'blue': 1, 'red': 0}
{'blue': 0, 'red': 1}
```

Each color becomes a pair of 0/1 columns. **Why one-hot and not just "red=1, blue=2"?** Because numbering categories invents a false order and distance (it would imply blue is "twice" red), which misleads the model. One-hot avoids that. (The tradeoff: many categories → many columns; for high-cardinality data you'd use target/embedding encoding instead.)

---

## Scaling and normalization (tested)

Features on different scales (age 0-100 vs income 0-1,000,000) can bias models that use distances or gradients. Two standard fixes:

**Min-max scaling** — squash to [0, 1]:

```python
def min_max_scale(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) for v in values]

print(min_max_scale([10, 20, 30]))
```

Output:

```text
[0.0, 0.5, 1.0]
```

**Standardization (z-score)** — center at 0 with unit standard deviation:

```python
def standardize(values):
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = var ** 0.5
    return [(v - mean) / std for v in values]

print([round(z, 3) for z in standardize([2, 4, 6])])
```

Output:

```text
[-1.225, 0.0, 1.225]
```

Standardized data has mean 0 and std 1. **When to use which:** min-max keeps values bounded (good for neural nets, image pixels); standardization handles outliers better and suits distance/gradient methods (SVM, linear/logistic regression, k-means). Many models (tree-based ones) don't need scaling at all.

---

## Creating features

Often the biggest wins come from *creating* features from domain knowledge:

- **Combinations** — `price_per_sqft = price / area`; ratios and interactions often capture what raw columns don't.
- **Datetime parts** — extract day-of-week, month, is_weekend, hour from a timestamp (behavior varies by these).
- **Binning** — group a continuous value into ranges (age → "child/adult/senior").
- **Aggregations** — per-user averages, counts, recency.
- **Text** — word counts, TF-IDF, embeddings (see the AI & LLMs section).

This is where domain understanding turns into predictive power — a model can only learn from what you give it.

---

## Feature selection

More features isn't always better — irrelevant ones add noise and overfitting risk. Selection keeps the useful ones:

- **Filter** — rank features by correlation/statistical test with the target, keep the top.
- **Wrapper** — try subsets, measure model performance (e.g. recursive feature elimination).
- **Embedded** — the model selects during training (L1/Lasso regularization zeroes out weak features).

---

## In practice: scikit-learn

Real pipelines use scikit-learn's transformers, which fit on training data and apply consistently to new data:

```python
from sklearn.preprocessing import OneHotEncoder, StandardScaler   # pip install scikit-learn
from sklearn.pipeline import Pipeline

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)     # learn mean/std from train
X_test_scaled = scaler.transform(X_test)     # apply SAME transform to test
```

!!! note "scikit-learn snippet follows documented API"
    scikit-learn isn't installed here (the pure-Python transforms are run-verified). Its transformers are the standard tools — but note the critical pattern: **fit on training data, then apply to test data**. Computing the scaling from the whole dataset (including test) leaks information and inflates your results — a classic mistake.

!!! warning "Beware data leakage"
    The #1 feature-engineering pitfall: **leakage** — using information at training time that wouldn't be available at prediction time (or fitting scalers/encoders on test data). It makes your model look great in evaluation and fail in production. Always fit transforms on training data only.

---

## Practice exercises

1. Extend `one_hot` to handle unseen categories at prediction time (all-zeros row).
2. Implement "robust scaling" using median and IQR instead of mean/std, and compare on data with an outlier.
3. Create a `price_per_unit` feature from price and quantity columns, handling division by zero.
4. Bin a list of ages into categories and one-hot encode the result.
5. Explain data leakage with a concrete example and how fit/transform separation prevents it.
