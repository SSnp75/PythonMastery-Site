---
title: Scikit-Learn
description: Machine learning models, pipelines, cross-validation, hyperparameter tuning and evaluation
---

# Scikit-Learn <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="../intermediate/numpy/">NumPy</a>, <a href="../intermediate/pandas/">Pandas</a></span>
  </div>
</div>

---

## The sklearn workflow

```
Load Data → Split → Preprocess → Train → Predict → Evaluate
```

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import load_iris

# 1. Load data
iris = load_iris()
X, y = iris.data, iris.target

# 2. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Preprocess
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit + transform
X_test_scaled = scaler.transform(X_test)          # only transform!

# 4. Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# 5. Predict
y_pred = model.predict(X_test_scaled)

# 6. Evaluate
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

Output:
```
Accuracy: 1.0000
              precision    recall  f1-score   support
      setosa       1.00      1.00      1.00        10
  versicolor       1.00      1.00      1.00        10
   virginica       1.00      1.00      1.00        10
    accuracy                           1.00        30
```

---

## Pipelines — the right way

Pipelines prevent data leakage and simplify deployment:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

# Define feature groups
numeric_features = ["age", "income", "credit_score"]
categorical_features = ["city", "education", "employment"]

# Build preprocessing pipelines
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

# Combine with ColumnTransformer
preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numeric_features),
    ("cat", categorical_pipeline, categorical_features),
])

# Full pipeline: preprocessing + model
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", GradientBoostingClassifier(n_estimators=200, random_state=42)),
])

# Use it
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
score = pipeline.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")
```

---

## Cross-validation

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

# Simple cross-validation
scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
print(f"CV scores: {scores}")
print(f"Mean: {scores.mean():.4f} ± {scores.std():.4f}")

# More control with StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipeline, X, y, cv=skf, scoring="f1_macro")

# Multiple metrics
from sklearn.model_selection import cross_validate

results = cross_validate(
    pipeline, X, y, cv=5,
    scoring=["accuracy", "f1_macro", "roc_auc_ovr"],
    return_train_score=True,
)
print(f"Test accuracy: {results['test_accuracy'].mean():.4f}")
print(f"Test F1: {results['test_f1_macro'].mean():.4f}")
```

---

## Hyperparameter tuning

### GridSearchCV

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "classifier__n_estimators": [100, 200, 500],
    "classifier__max_depth": [3, 5, 7, None],
    "classifier__learning_rate": [0.01, 0.1, 0.3],
}

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring="f1_macro",
    n_jobs=-1,       # use all CPUs
    verbose=1,
)
grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.4f}")
best_model = grid_search.best_estimator_
```

### RandomizedSearchCV (faster for large search spaces)

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_distributions = {
    "classifier__n_estimators": randint(50, 500),
    "classifier__max_depth": randint(2, 20),
    "classifier__learning_rate": uniform(0.001, 0.5),
    "classifier__subsample": uniform(0.5, 0.5),
}

random_search = RandomizedSearchCV(
    pipeline,
    param_distributions,
    n_iter=50,       # try 50 random combinations
    cv=5,
    scoring="f1_macro",
    n_jobs=-1,
    random_state=42,
)
random_search.fit(X_train, y_train)
```

---

## Model evaluation

### Classification metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve,
    classification_report
)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)   # probability scores

print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred, average='macro'):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred, average='macro'):.4f}")
print(f"F1:        {f1_score(y_test, y_pred, average='macro'):.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)
# [[10,  0,  0],
#  [ 0,  9,  1],
#  [ 0,  0, 10]]
```

### Regression metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print(f"MSE:  {mean_squared_error(y_test, y_pred):.4f}")
print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, y_pred):.4f}")
print(f"R²:   {r2_score(y_test, y_pred):.4f}")
```

---

## Feature importance

```python
# Tree-based models have built-in feature importance
importances = model.feature_importances_
feature_names = X.columns if hasattr(X, "columns") else [f"f{i}" for i in range(X.shape[1])]

# Sort and display
sorted_idx = np.argsort(importances)[::-1]
for i in sorted_idx[:10]:
    print(f"  {feature_names[i]}: {importances[i]:.4f}")

# Permutation importance (model-agnostic)
from sklearn.inspection import permutation_importance

perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
for i in perm_importance.importances_mean.argsort()[::-1][:10]:
    print(f"  {feature_names[i]}: {perm_importance.importances_mean[i]:.4f} "
          f"± {perm_importance.importances_std[i]:.4f}")
```

---

## Common algorithms cheat sheet

| Algorithm | Type | Use case |
|---|---|---|
| `LogisticRegression` | Classification | Linear boundary, baseline |
| `RandomForestClassifier` | Classification | Non-linear, feature importance |
| `GradientBoostingClassifier` | Classification | Best accuracy, competitions |
| `SVC` | Classification | Small datasets, kernel trick |
| `KNeighborsClassifier` | Classification | Simple, no training |
| `LinearRegression` | Regression | Linear relationships |
| `RandomForestRegressor` | Regression | Non-linear, robust |
| `GradientBoostingRegressor` | Regression | Best accuracy |
| `KMeans` | Clustering | Unsupervised grouping |
| `DBSCAN` | Clustering | Density-based, arbitrary shapes |
| `PCA` | Dimensionality reduction | Feature reduction, visualization |

---

## Saving and loading models

```python
import joblib

# Save
joblib.dump(pipeline, "model_v1.joblib")

# Load
loaded_pipeline = joblib.load("model_v1.joblib")
predictions = loaded_pipeline.predict(new_data)
```

---

## Practice Exercises

1. **Build a complete ML pipeline** for a binary classification problem with proper preprocessing.
2. **Compare 5 algorithms** on the same dataset using cross-validation and report the best.
3. **Tune hyperparameters** with RandomizedSearchCV and plot the learning curve.
4. **Handle imbalanced classes** using SMOTE, class weights, or threshold tuning.
5. **Build a regression model** for house prices and interpret feature importances.
6. **Implement k-fold cross-validation** from scratch (without sklearn) to understand how it works.
7. **Create an end-to-end pipeline** that preprocesses, trains, evaluates, and saves a model.
