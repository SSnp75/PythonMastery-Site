---
title: "ML Inference Graphs"
description: Orchestrate multi-step inference pipelines as DAGs for latency and throughput
---

# ML Inference Graphs <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="ml-deployment.md">ML Deployment</a>, <a href="../../web/expert/microservices.md">Microservices</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why real inference is multi-step
- [x] Model an inference pipeline as a DAG (tested)
- [x] Latency vs throughput tradeoffs
- [x] Serving frameworks

Real-world ML inference is rarely a single model call. A request flows through preprocessing, maybe several models, and postprocessing — a **graph** of steps. Structuring this well determines latency and throughput. The DAG execution logic here is **run-verified**.

---

## Inference is a pipeline, not one call

Serving a prediction usually involves multiple stages:

```
   request → preprocess → model A → ┐
                                    ├→ combine → postprocess → response
             preprocess → model B → ┘
```

For example: tokenize text → embed it → run a classifier *and* a sentiment model → merge results → format. These steps form a **directed acyclic graph (DAG)** — some run in sequence, some can run in parallel.

---

## Modeling a pipeline as a DAG (tested)

At its core, orchestrating this is topological execution of a dependency graph — the same idea as a build system or [data pipeline](../../projects/advanced.md). Runnable:

```python
def run_graph(nodes, inputs):
    """nodes: name -> (func, [dependency names]). Execute in dependency order."""
    results = dict(inputs)
    done = set(inputs)
    pending = dict(nodes)
    while pending:
        ran_any = False
        for name, (func, deps) in list(pending.items()):
            if all(d in done for d in deps):          # deps ready?
                args = [results[d] for d in deps]
                results[name] = func(*args)
                done.add(name)
                del pending[name]
                ran_any = True
        if not ran_any:
            raise ValueError("cycle or missing dependency")
    return results

# A tiny inference graph: preprocess -> (modelA, modelB) -> combine
graph = {
    "pre":    (lambda x: x.strip().lower(), ["raw"]),
    "modelA": (lambda t: len(t), ["pre"]),           # e.g. length feature
    "modelB": (lambda t: t.count("a"), ["pre"]),     # e.g. 'a' count
    "combine":(lambda a, b: {"len": a, "a_count": b}, ["modelA", "modelB"]),
}
out = run_graph(graph, {"raw": "  BANANA  "})
print(out["combine"])
```

Output:

```text
{'len': 6, 'a_count': 3}
```

The executor runs each node once its dependencies are ready: `pre` first, then `modelA`/`modelB` (both depend only on `pre`, so they *could* run in parallel), then `combine`. This dependency-driven execution — the heart of every inference-serving graph and workflow engine — ensures correct ordering and exposes what can be parallelized.

---

## Latency vs throughput

Two competing goals shape inference-graph design:

- **Latency** — time for *one* request. Minimize by running independent nodes in **parallel** (`modelA` and `modelB` at once) and keeping the critical path short.
- **Throughput** — requests *per second*. Maximize by **batching** — grouping many requests so the GPU processes them together (GPUs are far more efficient on batches). But batching *adds* latency (waiting to fill a batch).

```
   Low latency:   process each request immediately (small/no batch)
   High throughput: wait, batch many requests, process together
                    ← the fundamental tradeoff (dynamic batching balances it)
```

**Dynamic batching** (used by serving frameworks) balances these: wait a few milliseconds to gather a batch, but no longer, capping added latency while gaining throughput.

---

## Serving frameworks

You don't build production serving graphs from scratch — frameworks handle DAG orchestration, batching, and scaling (documented; not installed here):

| Framework | Notes |
|---|---|
| **NVIDIA Triton Inference Server** | Multi-model serving, dynamic batching, model ensembles (DAGs) |
| **Ray Serve** | Python-native, composable deployment graphs |
| **BentoML** | Package + serve models with pipelines |
| **TorchServe / TF Serving** | Framework-specific serving |
| **Seldon / KServe** | Kubernetes-native inference graphs |

These let you declare the graph, and they manage parallelism, batching, autoscaling, and versioning.

!!! tip "It's an orchestration problem"
    Once models are optimized ([ONNX & TensorRT](onnx-tensorrt.md), [Quantization](quantization.md)), serving becomes an *orchestration* problem — the same DAG/dependency thinking as build systems, [data pipelines](../../projects/advanced.md), and [microservices](../../web/expert/microservices.md). The tested executor above is that idea in miniature; frameworks scale it with batching and distribution.

---

## Practice exercises

1. Add a `postprocess` node to the graph that depends on `combine`, and run it.
2. Modify `run_graph` to record which nodes *could* have run in parallel (same dependency level).
3. Explain the latency/throughput tradeoff and how dynamic batching balances it.
4. Add cycle detection that reports *which* nodes form the cycle.
5. Describe how you'd serve a two-model ensemble with a real framework (Triton or Ray Serve).
