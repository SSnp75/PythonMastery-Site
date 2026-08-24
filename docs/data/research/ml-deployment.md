---
title: ML Deployment
description: Triton server, BentoML, Ray Serve, ONNX, containerization and production inference
---

# ML Deployment <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisite: <a href="../proficient/ml-pipelines/">ML Pipelines</a></span>
  </div>
</div>

---

## Deployment landscape

| Tool | Best for | Latency | Throughput |
|---|---|---|---|
| **FastAPI + uvicorn** | Simple models, prototypes | Low | Moderate |
| **BentoML** | Packaging + serving | Low | High |
| **Ray Serve** | Scalable, multi-model | Low | Very high |
| **Triton Inference Server** | GPU inference at scale | Very low | Very high |
| **TorchServe** | PyTorch-specific | Low | High |
| **TFServing** | TensorFlow-specific | Low | High |

---

## Model export: ONNX

Convert models to a portable format:

```python
import torch
import torch.onnx

model = MyModel()
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["image"],
    output_names=["prediction"],
    dynamic_axes={"image": {0: "batch_size"}, "prediction": {0: "batch_size"}},
    opset_version=17,
)

# Verify
import onnx
model_onnx = onnx.load("model.onnx")
onnx.checker.check_model(model_onnx)

# Inference with ONNX Runtime
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("model.onnx")
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
outputs = session.run(None, {"image": input_data})
print(outputs[0].shape)   # (1, 1000)
```

---

## BentoML — package and serve

```python
# save_model.py
import bentoml
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Save to BentoML model store
saved_model = bentoml.sklearn.save_model("churn_classifier", model)
print(f"Saved: {saved_model.tag}")   # churn_classifier:abc123

# service.py
import bentoml
import numpy as np
from bentoml.io import NumpyNdarray, JSON

runner = bentoml.sklearn.get("churn_classifier:latest").to_runner()
svc = bentoml.Service("churn_service", runners=[runner])

@svc.api(input=NumpyNdarray(), output=JSON())
async def predict(input_array: np.ndarray):
    prediction = await runner.predict.async_run(input_array)
    return {"prediction": prediction.tolist()}
```

```bash
# Serve locally
bentoml serve service.py:svc --reload

# Build container
bentoml build
bentoml containerize churn_service:latest

# Deploy
docker run -p 3000:3000 churn_service:latest
```

---

## Ray Serve — scalable serving

```python
from ray import serve
from ray.serve.handle import DeploymentHandle
import numpy as np

@serve.deployment(num_replicas=2, ray_actor_options={"num_gpus": 0.5})
class ModelDeployment:
    def __init__(self):
        import joblib
        self.model = joblib.load("model.joblib")

    async def __call__(self, request):
        data = await request.json()
        features = np.array(data["features"]).reshape(1, -1)
        prediction = self.model.predict(features)
        probability = self.model.predict_proba(features).max()
        return {
            "prediction": int(prediction[0]),
            "confidence": float(probability),
        }

# Compose multiple models
@serve.deployment
class Ensemble:
    def __init__(self, model_a: DeploymentHandle, model_b: DeploymentHandle):
        self.model_a = model_a
        self.model_b = model_b

    async def __call__(self, request):
        # Run both models in parallel
        ref_a = self.model_a.remote(request)
        ref_b = self.model_b.remote(request)
        result_a, result_b = await ref_a, await ref_b
        # Average predictions
        return {"prediction": (result_a["prediction"] + result_b["prediction"]) / 2}

# Deploy
app = ModelDeployment.bind()
serve.run(app, host="0.0.0.0", port=8000)
```

---

## Monitoring and drift detection

```python
import numpy as np
from scipy.stats import ks_2samp

class DriftDetector:
    def __init__(self, reference_data: np.ndarray, threshold=0.05):
        self.reference = reference_data
        self.threshold = threshold

    def check_drift(self, current_data: np.ndarray) -> dict:
        results = {}
        for i in range(current_data.shape[1]):
            stat, p_value = ks_2samp(self.reference[:, i], current_data[:, i])
            results[f"feature_{i}"] = {
                "statistic": float(stat),
                "p_value": float(p_value),
                "drift_detected": p_value < self.threshold,
            }
        return results

# Usage
detector = DriftDetector(X_train)
drift_report = detector.check_drift(X_new_batch)
drifted = [k for k, v in drift_report.items() if v["drift_detected"]]
if drifted:
    print(f"⚠️ Drift detected in: {drifted}")
    # Trigger retraining pipeline
```

---

## A/B testing models

```python
import random

class ModelRouter:
    def __init__(self, models: dict, traffic_split: dict):
        self.models = models          # {"v1": model_v1, "v2": model_v2}
        self.traffic_split = traffic_split  # {"v1": 0.9, "v2": 0.1}

    def predict(self, features):
        # Route based on traffic split
        r = random.random()
        cumulative = 0
        for version, weight in self.traffic_split.items():
            cumulative += weight
            if r <= cumulative:
                model = self.models[version]
                prediction = model.predict(features)
                self._log_prediction(version, features, prediction)
                return {"prediction": prediction, "model_version": version}

    def _log_prediction(self, version, features, prediction):
        # Log to tracking system for later analysis
        pass

router = ModelRouter(
    models={"v1": model_old, "v2": model_new},
    traffic_split={"v1": 0.9, "v2": 0.1},  # 10% to new model
)
```

---

## Docker deployment pattern

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ ./model/
COPY serve.py .

EXPOSE 8000
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
services:
  model-api:
    build: .
    ports: ["8000:8000"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## Practice Exercises

1. **Export a PyTorch model** to ONNX and compare inference speed with ONNX Runtime vs native PyTorch.
2. **Build a BentoML service** with preprocessing, prediction and postprocessing.
3. **Implement drift detection** using KS-test on each feature and trigger alerts.
4. **Set up A/B testing** with 90/10 traffic split and log metrics for comparison.
5. **Dockerize a model API** with health checks, proper logging and GPU support.
6. **Implement a model registry** that tracks versions, metrics and deployment status.
