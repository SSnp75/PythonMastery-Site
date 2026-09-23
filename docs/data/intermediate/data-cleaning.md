---
title: "Data Cleaning"
description: Handle missing values, wrong types and outliers before analysis
---

# Data Cleaning <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="pandas.md">Pandas</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why cleaning is most of the work
- [x] Handle missing values (tested)
- [x] Fix wrong types (tested)
- [x] Detect and remove outliers (tested)
- [x] Validate data

"Data scientists spend 80% of their time cleaning data" is a cliché because it's true. Real data is messy — missing, malformed, and full of surprises. The core techniques here are shown in **run-verified** pure Python; in practice you'd use Pandas, which vectorizes them.

---

## Missing values (tested)

Real datasets have gaps. You either drop rows with missing data or **impute** (fill) them — commonly with the mean or median of the column. Runnable:

```python
def fill_missing(rows, column, strategy="mean"):
    values = [r[column] for r in rows if r[column] is not None]
    if strategy == "mean":
        fill = sum(values) / len(values)
    elif strategy == "median":
        s = sorted(values); n = len(s)
        fill = s[n//2] if n % 2 else (s[n//2 - 1] + s[n//2]) / 2
    for r in rows:
        if r[column] is None:
            r[column] = fill
    return rows

data = [{"age": 30}, {"age": None}, {"age": 50}, {"age": 40}]
fill_missing(data, "age", "mean")
print([r["age"] for r in data])
```

Output:

```text
[30, 40.0, 50, 40]
```

The missing age was filled with 40.0 (the mean of 30, 50, 40). **Choosing a strategy matters:** mean is simple but skewed by outliers; median is robust; sometimes dropping the row or flagging "was missing" as its own feature is better. There's no universally right answer — it depends on *why* the data is missing.

---

## Wrong types (tested)

Data from CSVs, forms, and APIs arrives as strings, with junk mixed in. Coerce safely, with a fallback:

```python
def coerce_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

print([coerce_int(x) for x in ["5", "bad", None, "10"]])
```

Output:

```text
[5, 0, 0, 10]
```

Valid strings convert; `"bad"` and `None` fall back to the default instead of crashing. Real cleaning decides per case whether a bad value should become a default, be dropped, or flagged for review — silently defaulting can hide data-quality problems, so log what you coerce.

---

## Outliers (tested)

Extreme values can distort analysis. A standard detector is the **IQR method**: flag points far outside the middle 50% of the data. Runnable:

```python
def remove_outliers(values, k=1.5):
    s = sorted(values); n = len(s)
    q1 = s[n // 4]                    # first quartile
    q3 = s[(3 * n) // 4]              # third quartile
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return [v for v in values if lo <= v <= hi]

print(sorted(remove_outliers([10, 12, 11, 13, 100, 9, 11])))
```

Output:

```text
[9, 10, 11, 11, 12, 13]
```

The obvious outlier `100` is removed; the tightly-clustered values stay. **But be careful:** an outlier might be a data error *or* a genuine rare event you shouldn't discard (a fraud transaction, a real extreme). Investigate before deleting — don't blindly strip outliers.

---

## In practice: Pandas

Real cleaning uses Pandas, which does all of this on whole columns at once:

```python
import pandas as pd     # pip install pandas

df = pd.read_csv("data.csv")

df["age"].fillna(df["age"].mean(), inplace=True)   # impute missing
df["count"] = pd.to_numeric(df["count"], errors="coerce")  # coerce types
df.drop_duplicates(inplace=True)                    # remove dup rows
df = df[df["price"] > 0]                            # filter invalid
```

!!! note "Pandas snippet follows documented API"
    Pandas isn't installed here (the pure-Python logic above is run-verified). Pandas vectorizes these operations across millions of rows efficiently — see [Pandas](pandas.md). The concepts are identical; Pandas just does them fast and concisely.

---

## Validate your data

Beyond fixing, *verify* assumptions hold: values in expected ranges, no impossible entries (negative ages), required fields present, categories from a known set. Libraries like **pandera** and **Great Expectations** let you declare data "contracts" and fail loudly when data violates them — catching quality problems before they corrupt analysis.

!!! tip "Clean reproducibly, log everything"
    Make cleaning a scripted, repeatable pipeline (not manual edits) so it re-runs on new data. And **log what you changed** — how many rows dropped, values imputed, outliers removed. Silent cleaning hides problems; visible cleaning builds trust in the results.

---

## Practice exercises

1. Add a `"drop"` strategy to `fill_missing` that removes rows with missing values instead of filling.
2. Extend `coerce_int` to collect and return which values it had to default (a data-quality report).
3. Modify `remove_outliers` to *cap* outliers at the bounds (winsorize) instead of removing them.
4. Write a validator that checks a list of records for required fields and valid ranges, returning all violations.
5. Explain a situation where removing outliers would be a mistake, with a concrete example.
