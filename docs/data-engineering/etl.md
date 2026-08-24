---
title: ETL Pipelines
description: Extract-Transform-Load patterns, data validation and pipeline orchestration
---

# ETL Pipelines <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔄 Data Engineering · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## ETL pattern

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

# ─── EXTRACT ──────────────────────────────────────
def extract_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"  Extracted {len(df)} rows from {path}")
    return df

def extract_api(url: str) -> pd.DataFrame:
    import httpx
    data = httpx.get(url).json()
    return pd.DataFrame(data)

def extract_database(query: str, conn_string: str) -> pd.DataFrame:
    from sqlalchemy import create_engine
    engine = create_engine(conn_string)
    return pd.read_sql(query, engine)

# ─── TRANSFORM ────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Clean
    df = df.dropna(subset=["email"])
    df["email"] = df["email"].str.lower().str.strip()
    # Derive
    df["created_date"] = pd.to_datetime(df["created_at"]).dt.date
    df["is_premium"] = df["total_spend"] > 1000
    # Validate
    df = df[df["age"].between(0, 120)]
    print(f"  Transformed: {len(df)} rows remaining")
    return df

# ─── LOAD ─────────────────────────────────────────
def load_to_warehouse(df: pd.DataFrame, table: str, conn_string: str):
    from sqlalchemy import create_engine
    engine = create_engine(conn_string)
    df.to_sql(table, engine, if_exists="append", index=False, method="multi")
    print(f"  Loaded {len(df)} rows to {table}")

def load_to_parquet(df: pd.DataFrame, path: str):
    df.to_parquet(path, index=False, compression="snappy")
    print(f"  Saved to {path}")

# ─── PIPELINE ─────────────────────────────────────
def run_pipeline():
    print(f"Pipeline started: {datetime.now()}")
    raw = extract_csv("data/users.csv")
    clean = transform(raw)
    load_to_parquet(clean, f"output/users_{datetime.now():%Y%m%d}.parquet")
    print(f"Pipeline complete: {datetime.now()}")

run_pipeline()
```

---

## Data validation with Pandera

```python
import pandera as pa
from pandera import Column, Check, DataFrameSchema

schema = DataFrameSchema({
    "name": Column(str, Check.str_length(min_value=1)),
    "email": Column(str, Check.str_matches(r".+@.+\..+")),
    "age": Column(int, Check.in_range(0, 120)),
    "salary": Column(float, Check.greater_than(0)),
})

def validated_transform(df: pd.DataFrame) -> pd.DataFrame:
    schema.validate(df)   # raises SchemaError on invalid data
    return df

# Or decorator style
@pa.check_output(schema)
def transform_users(df: pd.DataFrame) -> pd.DataFrame:
    ...
```

---

## Incremental loading patterns

```python
def incremental_extract(conn_string: str, table: str, last_run: datetime) -> pd.DataFrame:
    """Only extract rows modified since last run."""
    query = f"SELECT * FROM {table} WHERE updated_at > '{last_run.isoformat()}'"
    return extract_database(query, conn_string)

def upsert(df: pd.DataFrame, table: str, key_col: str, engine):
    """Insert new rows, update existing ones."""
    from sqlalchemy import text
    for _, row in df.iterrows():
        engine.execute(text(f"""
            INSERT INTO {table} ({', '.join(row.index)})
            VALUES ({', '.join([':' + c for c in row.index])})
            ON CONFLICT ({key_col}) DO UPDATE SET
            {', '.join([f'{c} = EXCLUDED.{c}' for c in row.index if c != key_col])}
        """), dict(row))
```

---

## Practice Exercises

1. **Build a full ETL** — extract from CSV + API, transform (clean, derive fields), load to SQLite.
2. **Add data validation** with Pandera — reject invalid rows and log them separately.
3. **Implement incremental loading** — only process new/changed records.
4. **Handle failures gracefully** — retry logic, dead-letter queue for failed records.
5. **Build an idempotent pipeline** — running twice produces the same result.
