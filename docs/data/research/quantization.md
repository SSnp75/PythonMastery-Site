---
title: "Quantization"
description: Shrink and speed up models with lower-precision numbers
---

# Quantization <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../scientific/custom-autograd.md">Autograd</a>, ML basics</span>
  </div>
</div>

---

## What you'll learn

- [x] What quantization is and why it helps
- [x] Quantize/dequantize math (tested)
- [x] Post-training vs quantization-aware
- [x] The accuracy tradeoff
- [x] Tooling

**Quantization** represents a model's numbers with fewer bits — typically converting 32-bit floats to 8-bit integers. This shrinks the model ~4×, speeds up inference, and cuts power use, at a small accuracy cost. It's essential for deploying big models to phones, edge devices, and cost-sensitive servers. The quantize/dequantize math here is **run-verified**.

---

## Why quantization

A trained neural network is millions/billions of `float32` weights. That's a lot of memory and compute:

- **Size** — `float32` → `int8` is a **4× reduction**. A 400 MB model becomes ~100 MB.
- **Speed** — integer math is faster, and less data movement means less time (memory bandwidth often dominates).
- **Power** — critical for battery devices and data-center cost.

The catch: fewer bits means less precision, so you trade a little accuracy for big efficiency gains.

---

## The quantize/dequantize math (tested)

Quantization maps a float range onto a small integer range using a **scale** and a **zero-point**. Runnable:

```python
def quantize(values, bits=8):
    lo, hi = min(values), max(values)
    levels = 2 ** bits - 1                       # 255 for int8
    scale = (hi - lo) / levels
    q = [round((v - lo) / scale) for v in values]
    return q, scale, lo

def dequantize(q, scale, lo):
    return [x * scale + lo for x in q]

original = [0.0, 0.25, 0.5, 0.75, 1.0]
q, scale, lo = quantize(original)
recovered = dequantize(q, scale, lo)

print("int8 values:", q)
print("recovered:  ", [round(x, 4) for x in recovered])
```

Output:

```text
int8 values: [0, 64, 128, 191, 255]
recovered:   [0.0, 0.251, 0.502, 0.749, 1.0]
```

The floats are mapped to integers 0-255 (fitting in a byte), and dequantizing recovers values very close to the originals — the tiny differences (0.25 → 0.251) are **quantization error**. That error is the price of using 8 bits instead of 32; for most neural networks it barely affects predictions, because networks are robust to small perturbations.

---

## Post-training vs quantization-aware

Two ways to quantize a model:

- **Post-Training Quantization (PTQ)** — quantize an already-trained model. Fast and easy (no retraining), but can lose more accuracy. Often you feed a small "calibration" dataset to pick good scales.
- **Quantization-Aware Training (QAT)** — simulate quantization *during* training so the model learns to be robust to it. More work (retraining), but recovers most of the lost accuracy.

Rule of thumb: try PTQ first (cheap); if accuracy drops too much, use QAT.

---

## The accuracy tradeoff

!!! warning "Quantization is lossy — validate it"
    Lower precision *will* change outputs. For most models the accuracy drop from int8 is small (often <1%), but not always — some models and layers are sensitive. **Always measure accuracy after quantizing** on your validation set. Sometimes a mixed approach (keep sensitive layers in higher precision) is the right balance. Never ship a quantized model without checking it still performs.

Precision options form a spectrum: `float32` (full) → `float16`/`bfloat16` (half, common on GPUs) → `int8` (common for inference) → `int4` and below (aggressive, for huge LLMs, more accuracy risk).

---

## Tooling

Real quantization uses framework tools (documented; not installed here):

```python
# PyTorch post-training dynamic quantization (documented API)
import torch
quantized = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

| Tool | Use |
|---|---|
| **PyTorch quantization** | PTQ and QAT in PyTorch |
| **TensorFlow Lite** | Quantization for mobile/edge |
| **ONNX Runtime** | Quantize + run ([ONNX & TensorRT](onnx-tensorrt.md)) |
| **bitsandbytes / GPTQ / AWQ** | LLM quantization (4-bit and below) |

!!! note "Framework snippets follow documented APIs"
    PyTorch etc. aren't installed here (the quantize/dequantize math is run-verified). The frameworks handle per-layer scales, calibration, and hardware-optimized int8 kernels. Quantization is a big reason large LLMs can run on consumer GPUs — 4-bit quantization makes a model a quarter of its size.

---

## Practice exercises

1. Extend `quantize` to use a symmetric scheme (zero-point at 0) and compare error.
2. Quantize to 4 bits (`bits=4`) and measure how much the max error grows versus 8 bits.
3. Explain why neural networks tolerate quantization error better than, say, a checksum would.
4. Describe when you'd choose QAT over PTQ.
5. Explain how 4-bit quantization lets a large LLM fit on a smaller GPU, with rough size math.
