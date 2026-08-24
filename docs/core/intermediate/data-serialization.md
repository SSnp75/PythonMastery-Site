---
title: Data Serialization
description: JSON, YAML, pickle, msgpack and data interchange formats
---

# Data Serialization <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
  </div>
</div>

---

## JSON

```python
import json

data = {"name": "Alice", "scores": [95, 87, 92]}

# Serialize
json_str = json.dumps(data, indent=2)

# Deserialize
obj = json.loads(json_str)

# File I/O
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data.json", "r") as f:
    loaded = json.load(f)
```

---

## YAML

```python
import yaml  # pip install pyyaml

config = {"server": {"host": "0.0.0.0", "port": 8080}}

# Write
with open("config.yaml", "w") as f:
    yaml.dump(config, f)

# Read
with open("config.yaml", "r") as f:
    loaded = yaml.safe_load(f)
```

---

## pickle (Python-only, binary)

```python
import pickle

# Serialize any Python object
with open("model.pkl", "wb") as f:
    pickle.dump(complex_object, f)

with open("model.pkl", "rb") as f:
    obj = pickle.load(f)
```

!!! warning "Security"
    Never unpickle data from untrusted sources. Pickle can execute arbitrary code.

---

## When to use what

| Format | Human-readable | Language-agnostic | Speed | Use case |
|---|---|---|---|---|
| JSON | Yes | Yes | Good | APIs, config, web |
| YAML | Yes | Yes | Moderate | Config files |
| pickle | No | No | Fast | Python-internal caching |
| msgpack | No | Yes | Very fast | High-perf IPC |
