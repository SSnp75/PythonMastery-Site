---
title: ML Pipelines
description: End-to-end machine learning workflows from data to deployment with MLflow
---

# ML Pipelines <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="scikit-learn/">Scikit-Learn</a></span>
  </div>
</div>

---

## The ML lifecycle

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│  Data  │ →  │Feature │ →  │ Train  │ →  │Evaluate│ →  │ Deploy │
│Ingest  │    │Engineer│    │ Model  │    │& Select│    │& Monitor│
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     ↑                                                       │
     └───────────────── Feedback Loop ──────────────────────┘
```

---

## Custom transformers

```python
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

class DateFeatures(BaseEstimator, TransformerMixin):
    """Extract useful features from datetime columns."""

    def __init__(self, date_column):
        self.date_column = date_column

    def fit(self, X, y=None):
        return self   # nothing to learn

    def transform(self, X):
        X = X.copy()
        dt = pd.to_datetime(X[self.date_column])
        X["year"] = dt.dt.year
        X["month"] = dt.dt.month
        X["day_of_week"] = dt.dt.dayofweek
        X["is_weekend"] = dt.dt.dayofweek.isin([5, 6]).astype(int)
        X["quarter"] = dt.dt.quarter
        X = X.drop(columns=[self.date_column])
        return X


class OutlierClipper(BaseEstimator, TransformerMixin):
    """Clip outliers using IQR method."""

    def __init__(self, factor=1.5):
        self.factor = factor

    def fit(self, X, y=None):
        Q1 = np.percentile(X, 25, axis=0)
        Q3 = np.percentile(X, 75, axis=0)
        IQR = Q3 - Q1
        self.lower_ = Q1 - self.factor * IQR
        self.upper_ = Q3 + self.factor * IQR
        return self

    def transform(self, X):
        return np.clip(X, self.lower_, self.upper_)


class TargetEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical variable using target mean."""

    def __init__(self, smoothing=10):
        self.smoothing = smoothing

    def fit(self, X, y):
        self.global_mean_ = y.mean()
        self.mapping_ = {}
        for col in range(X.shape[1]):
            df = pd.DataFrame({"cat": X[:, col], "target": y})
            agg = df.groupby("cat")["target"].agg(["mean", "count"])
            smooth = (agg["count"] * agg["mean"] + self.smoothing * self.global_mean_) / \
                     (agg["count"] + self.smoothing)
            self.mapping_[col] = smooth.to_dict()
        return self

    def transform(self, X):
        result = np.zeros_like(X, dtype=float)
        for col in range(X.shape[1]):
            mapping = self.mapping_[col]
            result[:, col] = [mapping.get(v, self.global_mean_) for v in X[:, col]]
        return result
```

---

## Full production pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

# Define feature groups
numeric = ["age", "income", "credit_score", "balance"]
categorical = ["city", "education", "employment_type"]
date = ["signup_date"]

# Build pipeline
pipeline = Pipeline([
    # Step 1: Feature engineering
    ("dates", DateFeatures("signup_date")),

    # Step 2: Preprocessing
    ("preprocessor", ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clipper", OutlierClipper(factor=2.0)),
            ("scaler", StandardScaler()),
        ]), numeric),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical),
    ])),

    # Step 3: Feature selection
    ("feature_selection", SelectKBest(f_classif, k=20)),

    # Step 4: Model
    ("classifier", GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )),
])

# Train and evaluate
scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="roc_auc")
print(f"AUC: {scores.mean():.4f} ± {scores.std():.4f}")

pipeline.fit(X_train, y_train)
```

---

## Experiment tracking with MLflow

```python
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("customer_churn")

with mlflow.start_run(run_name="gradient_boosting_v3"):
    # Log parameters
    mlflow.log_params({
        "n_estimators": 200,
        "max_depth": 5,
        "learning_rate": 0.1,
        "feature_selection_k": 20,
    })

    # Train
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    # Log metrics
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc": roc_auc_score(y_test, y_proba),
    })

    # Log model
    mlflow.sklearn.log_model(pipeline, "model")

    # Log artifacts (plots, data samples, etc.)
    mlflow.log_artifact("feature_importance.png")

    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

---

## Model versioning and registry

```python
# Register a model
model_uri = f"runs:/{run_id}/model"
mv = mlflow.register_model(model_uri, "customer_churn_model")

# Transition to production
from mlflow.tracking import MlflowClient
client = MlflowClient()
client.transition_model_version_stage(
    name="customer_churn_model",
    version=mv.version,
    stage="Production",
)

# Load production model
model = mlflow.sklearn.load_model("models:/customer_churn_model/Production")
predictions = model.predict(new_data)
```

---

## Data validation

```python
import pandas as pd

def validate_input(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate input data before prediction."""
    errors = []

    # Check required columns
    required = ["age", "income", "credit_score", "city"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check ranges
    if (df["age"] < 0).any() or (df["age"] > 120).any():
        errors.append("age values out of range [0, 120]")

    if (df["income"] < 0).any():
        errors.append("income cannot be negative")

    # Check categoricals
    valid_cities = {"NYC", "LA", "Chicago", "Houston", "Phoenix"}
    invalid = set(df["city"].unique()) - valid_cities
    if invalid:
        errors.append(f"Unknown cities: {invalid}")

    # Check for excessive nulls
    null_pct = df.isnull().mean()
    high_null = null_pct[null_pct > 0.5].index.tolist()
    if high_null:
        errors.append(f"Columns with >50% nulls: {high_null}")

    return len(errors) == 0, errors
```

---

## Model serving

```python
# FastAPI model serving
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib

app = FastAPI()
model = joblib.load("model_v1.joblib")

class PredictionRequest(BaseModel):
    age: float
    income: float
    credit_score: float
    city: str
    education: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str = "v1"

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    import pandas as pd
    df = pd.DataFrame([request.model_dump()])

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0].max()

    return PredictionResponse(
        prediction=int(prediction),
        probability=float(probability),
    )
```

---

## Practice Exercises

1. **Write a custom transformer** that creates polynomial features for numeric columns.
2. **Build a pipeline** that handles mixed types (numeric, categorical, text, datetime).
3. **Set up MLflow** tracking locally and log 5 experiments with different hyperparameters.
4. **Implement data validation** that checks schema, ranges, and distributions before prediction.
5. **Build a model serving API** with FastAPI that handles batch predictions.
6. **Implement A/B testing** for two model versions with traffic splitting.
