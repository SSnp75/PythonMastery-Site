---
title: "ONNX & TensorRT"
description: Export and optimize trained models for fast, portable inference
---

# ONNX & TensorRT <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="ml-deployment.md">ML Deployment</a>, <a href="quantization.md">Quantization</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The training-to-inference gap
- [x] What ONNX is (a portable model format)
- [x] What TensorRT does (GPU optimization)
- [x] The export-and-optimize pipeline
- [x] When to use them

You train a model in PyTorch or TensorFlow — but for *inference* (serving predictions), you often want something faster and more portable. **ONNX** is a standard format to export models, and **TensorRT** is NVIDIA's engine to run them fast on GPUs.

!!! note "Inference-tooling topic"
    ONNX Runtime, TensorRT, and the ML frameworks aren't installed here; this page follows their documented workflows conceptually.

---

## The training-to-inference gap

Training and inference have different needs:

- **Training** — flexibility, autograd, experimentation. Framework-specific (PyTorch, TF).
- **Inference** — speed, low latency, small footprint, running *anywhere* (server, mobile, browser, edge). You don't need autograd or training machinery.

Shipping your full training framework to production is heavy and slow. The fix: **export** the trained model to an optimized, portable form.

---

## ONNX: a portable model format

**ONNX** (Open Neural Network Exchange) is a standard file format for models. Train in one framework, export to ONNX, run *anywhere* that supports ONNX — decoupling training from serving.

```python
# Export a PyTorch model to ONNX (documented API)
import torch
torch.onnx.export(model, example_input, "model.onnx")

# Run it with ONNX Runtime — no PyTorch needed
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
outputs = session.run(None, {"input": data})
```

```
   PyTorch/TF model ──export──▶ model.onnx ──run on──▶ ONNX Runtime
                                              (CPU, GPU, mobile, browser, edge)
```

**Why it's valuable:** one exported `.onnx` file runs via **ONNX Runtime** on almost any hardware, often faster than the original framework because ONNX Runtime applies graph optimizations (operator fusion, constant folding). It also frees you from shipping the training framework to production.

---

## TensorRT: maximum GPU speed

**TensorRT** (NVIDIA) takes optimization further specifically for NVIDIA GPUs. It compiles a model into a highly-optimized inference "engine" using:

- **Layer fusion** — combine operations into single GPU kernels (fewer memory round-trips — echoing [GPU Kernels](../../systems/advanced/gpu-kernels-triton.md)).
- **Precision calibration** — run in FP16 or INT8 ([Quantization](quantization.md)) for big speedups.
- **Kernel auto-tuning** — pick the fastest kernel for your specific GPU.
- **Memory optimization** — reuse buffers.

The result can be several times faster than the original model on the same GPU — critical for high-throughput or low-latency serving.

---

## The export-and-optimize pipeline

A typical production path:

```
   1. Train (PyTorch/TF)
   2. Export to ONNX
   3. (optional) Quantize
   4. Optimize with ONNX Runtime  — or —  compile with TensorRT (NVIDIA GPUs)
   5. Serve the optimized model  (see ML Deployment / ML Inference Graphs)
```

Each step trades flexibility for speed. You lock in the model (no more training) in exchange for a lean, fast artifact.

!!! note "Snippets follow documented APIs"
    None of these run here (they need the libraries + often a GPU). The ONNX export/run and TensorRT compilation are shown per their documented usage. The idea to retain: **train flexible, serve optimized** — export to a portable/optimized form for production.

---

## When to use them

- **ONNX** — almost always worth it for production inference: portability + free graph optimizations, and it decouples serving from your training framework. Especially valuable for cross-platform (mobile, browser via ONNX Runtime Web, edge).
- **TensorRT** — when you serve on NVIDIA GPUs and need maximum throughput/lowest latency, and can invest in the (NVIDIA-specific) optimization step.

They compose: export to ONNX, then optionally compile that to a TensorRT engine. Connects to [ML Deployment](ml-deployment.md) and [ML Inference Graphs](ml-inference-graphs.md).

---

## Practice exercises

1. Explain why you'd export a model to ONNX instead of shipping the PyTorch training code.
2. List three optimizations ONNX Runtime or TensorRT applies and why each speeds inference.
3. Describe how quantization fits into the export-and-optimize pipeline.
4. Explain the tradeoff you accept when compiling to a fixed TensorRT engine.
5. Decide: for a model served in a browser vs on an NVIDIA server, which tooling fits each?
