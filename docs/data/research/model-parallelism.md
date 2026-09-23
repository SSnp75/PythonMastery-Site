---
title: "Model Parallelism"
description: Split a model too big for one device across multiple GPUs
---

# Model Parallelism <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="distributed-training.md">Distributed Training</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Data parallelism vs model parallelism
- [x] When a model doesn't fit on one GPU
- [x] Tensor and layer splitting
- [x] The communication cost
- [x] Frameworks

Modern models (large LLMs) can be too big to fit in a single GPU's memory. **Model parallelism** splits the *model itself* across multiple devices. This contrasts with data parallelism, which splits the *data*.

!!! note "This is a GPU/distributed topic"
    Model parallelism requires multiple GPUs and frameworks (PyTorch, DeepSpeed, Megatron) not available here. This page is conceptual, following documented framework approaches.

---

## Data vs model parallelism

Two fundamentally different ways to parallelize training:

```
   DATA PARALLELISM                    MODEL PARALLELISM
   same model on each GPU               model SPLIT across GPUs
   different data batch per GPU         same data flows through the pieces
   [model][model][model]                [layer1-2][layer3-4][layer5-6]
     GPU0    GPU1   GPU2                    GPU0      GPU1      GPU2
   → for models that FIT on one GPU      → for models TOO BIG for one GPU
```

- **Data parallelism** (see [Distributed Training](distributed-training.md)) — replicate the whole model on each GPU, feed each a different slice of the batch, average the gradients. Simple and common — but requires the model to *fit* on one GPU.
- **Model parallelism** — when the model is too big to fit, split it across GPUs.

---

## Ways to split a model

- **Tensor parallelism** — split *individual layers* across GPUs. A big matrix multiply is divided so each GPU computes part of it, then results are combined. Fine-grained; heavy communication.
- **Layer (pipeline) parallelism** — put *different layers* on different GPUs. Layer 1-2 on GPU0, 3-4 on GPU1, etc. Data flows through like an assembly line (see [Pipeline Parallelism](pipeline-parallelism.md)).
- **Expert parallelism** — for mixture-of-experts models, put different "expert" sub-networks on different GPUs.

Large-model training often combines all of these ("3D parallelism": data + tensor + pipeline).

---

## The communication cost

!!! warning "Communication is the bottleneck"
    Splitting a model means GPUs must constantly exchange intermediate results over their interconnect. This communication can dominate — a naive split can be *slower* than one GPU because the devices spend more time talking than computing. The engineering challenge is minimizing and overlapping communication with computation. This is why high-end training uses fast interconnects (NVLink, InfiniBand) — the network, not the math, is often the limit.

---

## Frameworks

You don't implement this by hand — specialized frameworks do (documented; not installed here):

| Framework | Role |
|---|---|
| **PyTorch FSDP** | Fully Sharded Data Parallel — shards model across GPUs |
| **DeepSpeed** (Microsoft) | ZeRO optimizer sharding, pipeline + tensor parallelism |
| **Megatron-LM** (NVIDIA) | Tensor/pipeline parallelism for huge transformers |
| **torch.distributed** | The lower-level primitives |

```python
# PyTorch FSDP (documented API)
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
model = FSDP(model)     # shards params/gradients/optimizer state across GPUs
```

These handle the splitting, communication, and gradient synchronization so you configure rather than hand-code it.

---

## When you need it

- **You need it** when a model + its activations + optimizer state exceed one GPU's memory (large LLMs, huge vision models).
- **You don't** for models that fit on one GPU — use simpler data parallelism to go faster.

Most practitioners use data parallelism; model parallelism is for the frontier of large-model training. It connects directly to [Pipeline Parallelism](pipeline-parallelism.md) (one splitting strategy) and [Distributed Training](distributed-training.md) (the broader topic).

---

## Practice exercises

1. Explain the difference between data and model parallelism and when each applies.
2. Describe why communication cost can make a naive model split slower than a single GPU.
3. Compare tensor parallelism (split within a layer) and pipeline parallelism (split across layers).
4. Estimate roughly: a model with 10B float32 params needs how much memory just for weights? Why might it not fit on one GPU?
5. Research PyTorch FSDP or DeepSpeed ZeRO and summarize what it shards across GPUs.
