---
title: "PyTorch C++ Ops"
description: Write custom high-performance PyTorch operators in C++/CUDA
---

# PyTorch C++ Ops <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../../systems/advanced/cpp-extensions.md">C++ Extensions</a>, <a href="../../scientific/custom-autograd.md">Autograd</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why write custom PyTorch operators
- [x] The C++ extension mechanism
- [x] Registering a custom op
- [x] Custom autograd (forward + backward)
- [x] When it's worth it

Sometimes PyTorch's built-in operations aren't enough — you need a **custom operator** for a novel computation or maximum speed. PyTorch lets you write ops in **C++/CUDA** and call them from Python as if native. This extends the general [C++ Extensions](../../systems/advanced/cpp-extensions.md) topic to PyTorch specifically.

!!! note "Requires PyTorch + a C++ toolchain"
    Building PyTorch C++ ops needs PyTorch, a compiler, and often CUDA — none present here. This page follows PyTorch's documented extension API conceptually.

---

## Why custom operators

Reasons to drop from Python into C++/CUDA for a PyTorch op:

- **Speed** — a fused custom kernel avoids the overhead of composing many small PyTorch ops (each of which launches a GPU kernel and moves memory).
- **Novel operations** — implement something PyTorch doesn't provide (a new attention variant, a custom loss).
- **Kernel fusion** — combine several operations into one GPU pass, avoiding intermediate memory traffic (like [GPU Kernels](../../systems/advanced/gpu-kernels-triton.md)).

The pattern is the familiar one: Python for the model, C++/CUDA for the hot custom op.

---

## The extension mechanism

PyTorch exposes its tensor library (ATen) to C++, so your operator works with PyTorch tensors directly:

```cpp
// custom_op.cpp
#include <torch/extension.h>

torch::Tensor custom_add(torch::Tensor a, torch::Tensor b) {
    return a + b;                      // uses PyTorch's tensor ops in C++
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("custom_add", &custom_add, "A custom add");
}
```

```python
import torch
from torch.utils.cpp_extension import load

# JIT-compile the C++ on first import
ext = load(name="ext", sources=["custom_op.cpp"])
result = ext.custom_add(torch.tensor([1.0]), torch.tensor([2.0]))   # -> tensor([3.])
```

PyTorch can compile the C++ just-in-time (`load`) or ahead-of-time via setuptools. It builds on **pybind11** (see [C++ Extensions](../../systems/advanced/cpp-extensions.md)) plus PyTorch's tensor types.

---

## Custom autograd (forward + backward)

The key ML-specific piece: for your op to work in training, it must support **backpropagation** — you provide both the forward computation and the gradient (backward). This is [autograd](../../scientific/custom-autograd.md) applied at the operator level:

```python
import torch

class CustomFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)       # remember inputs for backward
        return x * x                    # forward: y = x²

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        return grad_output * 2 * x      # backward: dy/dx = 2x
```

You define `forward` (the computation) and `backward` (its gradient) — exactly the pattern from the [autograd engine](../../scientific/custom-autograd.md) we built, but registered with PyTorch so it composes with the rest of the network. Get the backward math wrong and training silently breaks — so you *check gradients* against numerical differentiation (`torch.autograd.gradcheck`).

---

## When it's worth it

!!! tip "Last resort, big payoff"
    Writing C++/CUDA ops is a real investment (build systems, CUDA knowledge, gradient math, cross-platform wheels). Reach for it only when:
    - Profiling shows a custom op is a genuine bottleneck, **and**
    - You can't express it efficiently with existing PyTorch ops or `torch.compile`/Triton.

    First try: composing built-in ops, `torch.compile` (which fuses automatically), or a [Triton](../../systems/advanced/gpu-kernels-triton.md) kernel (Python-level GPU code, far easier than C++/CUDA). Custom C++ ops are the heaviest, most powerful rung — for research and production-critical kernels.

---

## Practice exercises

1. Explain why fusing several PyTorch ops into one custom kernel can be faster.
2. Describe why a custom op needs both forward and backward to be usable in training.
3. Relate PyTorch's `Function.forward`/`backward` to the autograd engine from the Scientific section.
4. Explain what `gradcheck` does and why you'd run it on a custom op.
5. Order these by effort for a custom fast op: built-in ops, Triton kernel, C++/CUDA op — and say when each is justified.
