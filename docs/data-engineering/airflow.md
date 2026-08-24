---
title: Apache Airflow
description: DAGs, operators, scheduling, dependencies and workflow orchestration
---

# Apache Airflow <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔄 Data Engineering · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## DAG (Directed Acyclic Graph)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["alerts@company.com"],
}

with DAG(
    dag_id="daily_etl_pipeline",
    default_args=default_args,
    description="Daily user data ETL",
    schedule_interval="0 6 * * *",   # 6 AM daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["etl", "users"],
) as dag:

    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_from_source,
    )

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    validate = PythonOperator(
        task_id="validate_data",
        python_callable=run_data_quality_checks,
    )

    load = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=load_to_bigquery,
    )

    notify = BashOperator(
        task_id="send_notification",
        bash_command='echo "ETL complete" | mail -s "Daily ETL" team@company.com',
    )

    # Define dependencies
    extract >> transform >> validate >> load >> notify
```

---

## TaskFlow API (Python-native, modern)

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def etl_pipeline():

    @task
    def extract() -> dict:
        """Extract data from source."""
        import pandas as pd
        df = pd.read_csv("s3://bucket/raw/users.csv")
        return {"rows": len(df), "path": "s3://bucket/raw/users.csv"}

    @task
    def transform(extract_result: dict) -> str:
        """Transform and save to staging."""
        import pandas as pd
        df = pd.read_csv(extract_result["path"])
        df["email"] = df["email"].str.lower()
        output_path = "s3://bucket/staging/users_clean.parquet"
        df.to_parquet(output_path)
        return output_path

    @task
    def load(path: str):
        """Load to data warehouse."""
        import pandas as pd
        df = pd.read_parquet(path)
        # load to BigQuery/Redshift...
        print(f"Loaded {len(df)} rows")

    # Automatic dependency inference
    data = extract()
    cleaned = transform(data)
    load(cleaned)

etl_pipeline()   # register the DAG
```

---

## Practice Exercises

1. **Build a DAG** with extract → transform → load → validate → notify.
2. **Add branching** — different transforms based on data characteristics.
3. **Implement retry and alerting** — 3 retries with exponential backoff, email on failure.
4. **Use XCom** to pass data between tasks.
5. **Schedule backfills** — process historical data for a date range.
