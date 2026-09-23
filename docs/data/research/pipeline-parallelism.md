---
title: "Pipeline Parallelism"
description: Split a model across GPUs like an assembly line, with micro-batching
---

# Pipeline Parallelism <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="model-parallelism.md">Model Parallelism</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What pipeline parallelism is
- [x] The idle-GPU ("bubble") problem
- [x] How micro-batching fixes it
- [x] Balancing the stages
- [x] Frameworks

**Pipeline parallelism** is a form of [model parallelism](model-parallelism.md) that puts *different layers* of a model on different GPUs, then streams data through them like a factory assembly line. Its central challenge — and clever fix — is keeping all GPUs busy.

!!! note "GPU/distributed topic"
    Requires multiple GPUs and frameworks not present here; this page is conceptual, following documented approaches.

---

## The assembly-line idea

Split the model's layers into **stages**, one per GPU:

```
   GPU0: layers 1-2  →  GPU1: layers 3-4  →  GPU2: layers 5-6
   data flows left to right (forward), gradients right to left (backward)
```

Each GPU handles its stage, passing activations to the next. This lets a model far larger than one GPU's memory train across several.

---

## The bubble problem

The naive version wastes most of the hardware:

```
   time →
   GPU0:  [fwd] ........................ [bwd]
   GPU1:  ..... [fwd] .............. [bwd] .....
   GPU2:  ......... [fwd] .... [bwd] ...........
          └── most GPUs IDLE most of the time ──┘
```

With one batch flowing through, while GPU0 works, GPU1 and GPU2 sit idle waiting — then GPU1 works while the others wait. This idle time is the **pipeline bubble**, and naively it wastes most of your expensive GPUs.

---

## Micro-batching: the fix

The solution is to split each batch into smaller **micro-batches** and feed them through in a staggered stream, so multiple stages work simultaneously:

```
   time →
   GPU0:  [mb1][mb2][mb3][mb4] ......
   GPU1:  ....[mb1][mb2][mb3][mb4] ...
   GPU2:  ........[mb1][mb2][mb3][mb4]
          └── stages overlap: all GPUs busy ──┘
```

Once the pipeline is "full," all GPUs process different micro-batches at once — like an assembly line where every station is working on a different unit. This dramatically shrinks the bubble. More micro-batches = smaller relative bubble, but with diminishing returns and memory costs. This scheme (GPipe/1F1B) is the heart of practical pipeline parallelism.

---

## Balancing the stages

!!! warning "Uneven stages waste the pipeline"
    A pipeline is only as fast as its slowest stage. If GPU1's layers take twice as long as the others, every GPU is throttled to its pace. **Balancing** — splitting layers so each stage takes roughly equal time — is essential. This is tricky because different layer types have very different costs, so frameworks provide auto-balancing or profiling to guide the split.

---

## Frameworks

Documented (not installed here):

| Framework | Notes |
|---|---|
| **PyTorch `torch.distributed.pipelining`** | Native pipeline parallelism |
| **DeepSpeed** | Pipeline + other parallelism, micro-batch scheduling |
| **Megatron-LM** | Combines pipeline with tensor parallelism |
| **GPipe / torchgpipe** | The technique's origin |

```python
# Conceptual: layers assigned to stages, micro-batches configured
# stage0 = layers[0:2] on GPU0
# stage1 = layers[2:4] on GPU1
# framework schedules micro-batches to overlap stages
```

---

## Where it fits

Pipeline parallelism is one tool in large-model training, usually **combined** with data parallelism and tensor parallelism ("3D parallelism") for the biggest models. Use pipeline parallelism when a model's layers won't fit on one GPU but split cleanly into sequential stages. See [Model Parallelism](model-parallelism.md) for the broader picture and [Distributed Training](distributed-training.md) for data parallelism.

---

## Practice exercises

1. Explain the pipeline bubble and why the naive one-batch approach wastes GPUs.
2. Describe how micro-batching reduces the bubble, and the tradeoff of using more micro-batches.
3. Explain why unbalanced stages throttle the whole pipeline to the slowest stage.
4. Draw (in text) the staggered schedule for 3 stages and 3 micro-batches.
5. Explain when you'd combine pipeline parallelism with tensor/data parallelism.
