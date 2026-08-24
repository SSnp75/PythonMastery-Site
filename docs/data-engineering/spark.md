---
title: PySpark
description: Distributed data processing with Spark DataFrames, SQL and transformations
---

# PySpark <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🔄 Data Engineering · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## PySpark basics

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .getOrCreate()

# ─── Read data ────────────────────────────────────
df = spark.read.csv("data/users.csv", header=True, inferSchema=True)
df = spark.read.parquet("s3://bucket/data/")
df = spark.read.json("data/events.json")

df.show(5)
df.printSchema()
print(f"Rows: {df.count()}, Columns: {len(df.columns)}")

# ─── Transformations ──────────────────────────────
result = (
    df
    .filter(F.col("age") > 18)
    .withColumn("full_name", F.concat(F.col("first"), F.lit(" "), F.col("last")))
    .withColumn("signup_year", F.year("created_at"))
    .groupBy("signup_year")
    .agg(
        F.count("*").alias("user_count"),
        F.avg("age").alias("avg_age"),
        F.sum("total_spend").alias("revenue"),
    )
    .orderBy(F.desc("revenue"))
)
result.show()

# ─── SQL interface ────────────────────────────────
df.createOrReplaceTempView("users")
spark.sql("""
    SELECT city, COUNT(*) as count, AVG(age) as avg_age
    FROM users
    WHERE age > 18
    GROUP BY city
    ORDER BY count DESC
    LIMIT 10
""").show()

# ─── Write ────────────────────────────────────────
result.write.parquet("output/user_stats/", mode="overwrite", partitionBy="signup_year")
```

---

## When Spark vs Pandas

| Feature | Pandas | PySpark |
|---|---|---|
| Data size | < 10 GB (fits in RAM) | Terabytes (distributed) |
| Execution | Single machine | Cluster (100s of nodes) |
| Speed (small data) | Faster | Slower (overhead) |
| Speed (big data) | Crashes (OOM) | Scales linearly |
| API | Rich, mature | Similar but not identical |

---

## Practice Exercises

1. **Process a large dataset** (>1GB) — filter, aggregate and save as partitioned Parquet.
2. **Join two datasets** and compute metrics across the join.
3. **Window functions** — rank users within each city by total spend.
4. **Optimize** — repartition, cache frequently-used DataFrames and reduce shuffles.
5. **Write a PySpark ETL** that reads from S3, transforms and writes back.
