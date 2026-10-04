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

*The default format for config and web APIs — human-readable and language-agnostic. Use `load`/`dump` for files, `loads`/`dumps` for strings.*

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

*A more human-friendly config format (used by Docker Compose, CI, k8s). Always use `safe_load` on untrusted input. Needs the third-party `pyyaml`.*

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

*Serialize almost any Python object to bytes — handy for caching and inter-process transfer within trusted Python code. Never unpickle untrusted data.*

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

## JSON round-trip (runnable)

*JSON round-trip (runnable) in Data Serialization — what it is and when to use it.*

```python
import json

data = {"name": "Alice", "scores": [95, 87, 92], "active": True}
s = json.dumps(data)
back = json.loads(s)
print(back == data)        # True
print(json.dumps({"a": 1}, sort_keys=True))   # {"a": 1}
```

Note the type mapping: Python `True` → JSON `true`, `None` → `null`, tuples → arrays.

---

## Custom JSON encoding

*Custom JSON encoding in Data Serialization — what it is and when to use it.*

`json` can't serialize arbitrary objects — supply a `default` function:

```python
import json
from datetime import date

def encode(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(type(obj).__name__)

print(json.dumps({"when": date(2026, 1, 15)}, default=encode))
# {"when": "2026-01-15"}
```

---

## CSV

*CSV in Data Serialization — what it is and when to use it.*

```python
import csv, io

buf = io.StringIO()
writer = csv.writer(buf)
writer.writerow(["name", "age"])
writer.writerow(["Alice", 30])

reader = csv.DictReader(io.StringIO(buf.getvalue()))
rows = list(reader)
print(rows)   # [{'name': 'Alice', 'age': '30'}]
```

CSV values are always strings on read — convert types yourself.

---

## TOML (read-only, stdlib 3.11+)

*TOML in Data Serialization — what it is and when to use it.*

```python
import tomllib   # Python 3.11+

doc = tomllib.loads('title = "demo"\n[server]\nport = 8080')
print(doc["server"]["port"])   # 8080
```

Great for config (`pyproject.toml` uses it). For writing TOML, use the `tomli-w` package.

---

## pickle round-trip (runnable)

*pickle round-trip (runnable) in Data Serialization — what it is and when to use it.*

```python
import pickle

obj = {"nums": [1, 2, 3], "nested": {"ok": True}}
blob = pickle.dumps(obj)          # bytes
restored = pickle.loads(blob)
print(restored == obj)            # True
```

!!! warning "pickle executes code"
    Never unpickle data from an untrusted source — a malicious payload can run arbitrary
    code during `loads`. Use JSON for anything crossing a trust boundary.

---

## When to use what

*A core question explored in Data Serialization: When to use what.*

| Format | Human-readable | Language-agnostic | Speed | Use case |
|---|---|---|---|---|
| JSON | Yes | Yes | Good | APIs, config, web |
| CSV | Yes | Yes | Good | tabular data, spreadsheets |
| TOML | Yes | Yes | Good | config files (pyproject.toml) |
| YAML | Yes | Yes | Moderate | config files |
| pickle | No | No | Fast | Python-internal caching (trusted) |
| msgpack | No | Yes | Very fast | high-perf IPC |
