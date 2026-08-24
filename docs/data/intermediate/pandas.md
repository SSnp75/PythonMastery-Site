---
title: Pandas
description: DataFrames, Series, groupby, merge, pivot, window functions and data manipulation
---

# Pandas <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="numpy/">NumPy</a></span>
  </div>
</div>

---

## DataFrame basics

```python
import pandas as pd
import numpy as np

# ─── Creating DataFrames ─────────────────────────
# From dict
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "age": [30, 25, 35, 28, 32],
    "city": ["NYC", "LA", "NYC", "Chicago", "LA"],
    "salary": [85000, 72000, 95000, 68000, 91000],
})
print(df)
#       name  age     city  salary
# 0    Alice   30      NYC   85000
# 1      Bob   25       LA   72000
# 2  Charlie   35      NYC   95000
# 3    Diana   28  Chicago   68000
# 4      Eve   32       LA   91000

# From CSV
df = pd.read_csv("data.csv")
df = pd.read_csv("data.csv", parse_dates=["date_col"], index_col="id")

# From JSON
df = pd.read_json("data.json")

# From SQL
import sqlite3
conn = sqlite3.connect("app.db")
df = pd.read_sql("SELECT * FROM users", conn)
```

---

## Inspecting data

```python
print(df.shape)        # (5, 4) — rows, columns
print(df.dtypes)       # data types per column
print(df.info())       # summary with null counts
print(df.describe())   # statistics for numeric columns
print(df.head(3))      # first 3 rows
print(df.tail(3))      # last 3 rows
print(df.columns)      # Index(['name', 'age', 'city', 'salary'])
print(df.index)        # RangeIndex(start=0, stop=5, step=1)
print(df.nunique())    # unique values per column
print(df.isnull().sum())  # null count per column
```

---

## Selecting data

```python
# ─── Column selection ─────────────────────────────
df["name"]              # Series
df[["name", "age"]]     # DataFrame (multiple columns)

# ─── Row selection ────────────────────────────────
df.iloc[0]              # first row by position
df.iloc[1:4]            # rows 1,2,3 by position
df.iloc[0, 2]           # row 0, column 2

df.loc[0]               # row with index label 0
df.loc[0, "name"]       # specific cell
df.loc[0:2, "name":"city"]  # slice by label (inclusive!)

# ─── Boolean filtering ────────────────────────────
df[df["age"] > 30]                          # age > 30
df[df["city"] == "NYC"]                     # city is NYC
df[(df["age"] > 25) & (df["salary"] > 80000)]  # combined (use & not 'and')
df[df["city"].isin(["NYC", "LA"])]          # city in list
df[df["name"].str.contains("li")]           # string contains

# ─── query() — SQL-like filtering ─────────────────
df.query("age > 30 and city == 'NYC'")
df.query("salary > @threshold")   # use variables with @
```

---

## Modifying data

```python
# ─── Add/modify columns ──────────────────────────
df["bonus"] = df["salary"] * 0.1
df["full_name"] = df["name"] + " Smith"
df["age_group"] = pd.cut(df["age"], bins=[20, 30, 40], labels=["20s", "30s"])

# Conditional assignment
df["senior"] = np.where(df["age"] >= 30, True, False)
df.loc[df["city"] == "NYC", "region"] = "East"

# ─── Rename columns ──────────────────────────────
df = df.rename(columns={"name": "full_name", "city": "location"})
df.columns = df.columns.str.lower()   # all lowercase

# ─── Drop columns/rows ───────────────────────────
df = df.drop(columns=["bonus"])
df = df.drop(index=[0, 1])   # drop rows by index

# ─── Sorting ─────────────────────────────────────
df = df.sort_values("salary", ascending=False)
df = df.sort_values(["city", "age"])   # multi-column sort

# ─── Reset index ─────────────────────────────────
df = df.reset_index(drop=True)
```

---

## GroupBy — split-apply-combine

```python
# ─── Basic groupby ────────────────────────────────
grouped = df.groupby("city")

# Aggregation
print(grouped["salary"].mean())
# city
# Chicago    68000.0
# LA         81500.0
# NYC        90000.0

# Multiple aggregations
stats = grouped["salary"].agg(["mean", "median", "std", "count"])
print(stats)

# Named aggregation (clearest syntax)
result = df.groupby("city").agg(
    avg_salary=("salary", "mean"),
    max_salary=("salary", "max"),
    headcount=("name", "count"),
    avg_age=("age", "mean"),
)
print(result)

# ─── Transform — return same-shape result ─────────
# Normalize salary within each city
df["salary_z"] = df.groupby("city")["salary"].transform(
    lambda x: (x - x.mean()) / x.std()
)

# ─── Filter — keep/drop groups ────────────────────
# Keep only cities with more than 1 person
df_filtered = df.groupby("city").filter(lambda g: len(g) > 1)

# ─── Apply — arbitrary function per group ─────────
def top_earner(group):
    return group.nlargest(1, "salary")

result = df.groupby("city").apply(top_earner).reset_index(drop=True)
```

---

## Merge / Join

```python
# ─── merge (SQL-style join) ───────────────────────
orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "user_id": [101, 102, 101, 103],
    "amount": [50, 30, 75, 20],
})

users = pd.DataFrame({
    "user_id": [101, 102, 104],
    "name": ["Alice", "Bob", "Diana"],
})

# Inner join (default) — only matching rows
inner = orders.merge(users, on="user_id")

# Left join — keep all left rows
left = orders.merge(users, on="user_id", how="left")

# Outer join — keep all rows from both
outer = orders.merge(users, on="user_id", how="outer")

# Different column names
orders.merge(users, left_on="user_id", right_on="user_id")

# ─── concat — stack DataFrames ────────────────────
df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
df2 = pd.DataFrame({"a": [5, 6], "b": [7, 8]})

vertical = pd.concat([df1, df2], ignore_index=True)   # stack vertically
horizontal = pd.concat([df1, df2], axis=1)             # side by side
```

---

## Pivot tables and reshaping

```python
# ─── pivot_table — aggregate and reshape ──────────
sales = pd.DataFrame({
    "date": ["Mon", "Mon", "Tue", "Tue", "Wed", "Wed"],
    "product": ["A", "B", "A", "B", "A", "B"],
    "revenue": [100, 150, 120, 130, 110, 140],
})

pivot = sales.pivot_table(
    values="revenue",
    index="date",
    columns="product",
    aggfunc="sum",
)
print(pivot)
# product    A    B
# date
# Mon      100  150
# Tue      120  130
# Wed      110  140

# ─── melt — wide to long ─────────────────────────
long = pivot.reset_index().melt(id_vars="date", var_name="product", value_name="revenue")

# ─── crosstab ────────────────────────────────────
pd.crosstab(df["city"], df["senior"])
```

---

## Window functions (rolling, expanding)

```python
# Time series data
dates = pd.date_range("2026-01-01", periods=30)
ts = pd.DataFrame({
    "date": dates,
    "value": np.random.randn(30).cumsum() + 100,
})
ts = ts.set_index("date")

# ─── Rolling window ──────────────────────────────
ts["ma_7"] = ts["value"].rolling(window=7).mean()     # 7-day moving average
ts["ma_14"] = ts["value"].rolling(window=14).mean()   # 14-day
ts["std_7"] = ts["value"].rolling(window=7).std()     # rolling std

# ─── Expanding (cumulative) ───────────────────────
ts["cummax"] = ts["value"].expanding().max()
ts["cummin"] = ts["value"].expanding().min()

# ─── Shift (lag/lead) ────────────────────────────
ts["prev_day"] = ts["value"].shift(1)       # yesterday's value
ts["next_day"] = ts["value"].shift(-1)      # tomorrow's value
ts["daily_change"] = ts["value"].diff()     # day-over-day change
ts["pct_change"] = ts["value"].pct_change() # percentage change

# ─── Rank ─────────────────────────────────────────
df["salary_rank"] = df["salary"].rank(ascending=False)
df["salary_rank_by_city"] = df.groupby("city")["salary"].rank(ascending=False)
```

---

## Handling missing data

```python
# Check for nulls
print(df.isnull().sum())
print(df.isna().any())

# Drop rows with any null
df_clean = df.dropna()
df_clean = df.dropna(subset=["salary", "age"])   # only check these columns

# Fill missing values
df["salary"] = df["salary"].fillna(df["salary"].median())
df["city"] = df["city"].fillna("Unknown")
df["age"] = df["age"].fillna(method="ffill")   # forward fill

# Interpolation (for time series)
df["value"] = df["value"].interpolate(method="linear")
```

---

## String operations

```python
# .str accessor for vectorized string operations
df["name_lower"] = df["name"].str.lower()
df["name_len"] = df["name"].str.len()
df["first_char"] = df["name"].str[0]
df["has_a"] = df["name"].str.contains("a", case=False)
df["name_parts"] = df["name"].str.split(" ")
df["domain"] = df["email"].str.extract(r"@(.+)")
df["city_clean"] = df["city"].str.strip().str.title()
```

---

## Performance optimization

```python
# 1. Use appropriate dtypes
df["category_col"] = df["category_col"].astype("category")   # saves memory
df["id"] = df["id"].astype("int32")   # use smaller int

# 2. Vectorized operations (avoid apply when possible)
# BAD (slow)
df["result"] = df["col"].apply(lambda x: x**2 + 1)
# GOOD (fast)
df["result"] = df["col"]**2 + 1

# 3. Use query() for complex filters (faster for large DataFrames)
df.query("age > 30 and salary > 80000")

# 4. Read only needed columns
df = pd.read_csv("huge.csv", usecols=["name", "age", "salary"])

# 5. Process in chunks
for chunk in pd.read_csv("huge.csv", chunksize=10000):
    process(chunk)
```

---

## Saving data

```python
# CSV
df.to_csv("output.csv", index=False)

# Excel
df.to_excel("output.xlsx", sheet_name="Sheet1", index=False)

# JSON
df.to_json("output.json", orient="records", indent=2)

# Parquet (fast, compressed — best for large data)
df.to_parquet("output.parquet")
df = pd.read_parquet("output.parquet")

# SQL
df.to_sql("users", conn, if_exists="replace", index=False)
```

---

## Practice Exercises

1. **Load a CSV** with 100K+ rows, inspect it, handle missing values and duplicates.
2. **GroupBy + Agg**: Find the top 5 categories by average revenue.
3. **Merge 3 tables** (users, orders, products) and compute total spend per user.
4. **Time series**: Compute 7-day and 30-day moving averages on stock prices.
5. **Pivot table**: Transform transaction data into a monthly revenue by product matrix.
6. **Performance**: Compare the speed of `.apply()` vs vectorized operations on 1M rows.
7. **Clean a messy dataset**: Parse dates, fix typos in categorical columns, handle outliers.
