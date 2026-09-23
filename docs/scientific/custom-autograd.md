---
title: "Custom Autograd Engines"
description: Build automatic differentiation from scratch — the engine behind deep learning
---

# Custom Autograd Engines <span class="pm-badge pm-badge-research">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: calculus (chain rule), <a href="numerical-optimization.md">Numerical Optimization</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What automatic differentiation is
- [x] Forward vs reverse mode
- [x] Build a working autograd engine (tested!)
- [x] How this powers PyTorch/JAX
- [x] Why it beats numerical/symbolic differentiation

**Automatic differentiation (autodiff)** computes exact derivatives of code automatically. It's the engine under every deep-learning framework — how a neural network knows which way to adjust millions of weights. Remarkably, a working autograd engine fits in ~30 lines, and the one here is **fully run-verified**.

---

## Three ways to differentiate

- **Numerical** — approximate via `(f(x+h) - f(x)) / h`. Simple but imprecise and slow (one evaluation per input).
- **Symbolic** — manipulate formulas algebraically (like SymPy). Exact but explodes in size for complex functions.
- **Automatic** — apply the chain rule to the actual operations as they execute. Exact *and* efficient. This is what frameworks use.

Autodiff wins by tracking each elementary operation and composing their known derivatives via the chain rule.

---

## Forward vs reverse mode

- **Forward mode** — propagate derivatives *from inputs toward outputs*. Efficient when there are few inputs, many outputs.
- **Reverse mode** — compute the output, then propagate gradients *backward from output to inputs*. Efficient when there are **many inputs, one output** — exactly the case in machine learning (millions of weights, one loss). This backward pass is **backpropagation**.

We'll build reverse mode, since it's what ML uses.

---

## A working autograd engine (tested)

Each `Value` remembers how it was computed and knows how to push gradients to its inputs. Runnable:

```python
class Value:
    """A scalar that tracks its gradient (reverse-mode autodiff)."""
    def __init__(self, data, _children=()):
        self.data = data
        self.grad = 0.0
        self._backward = lambda: None      # how to send grad to inputs
        self._prev = set(_children)

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other))
        def _backward():
            self.grad += out.grad          # d(a+b)/da = 1
            other.grad += out.grad         # d(a+b)/db = 1
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other))
        def _backward():
            self.grad += other.data * out.grad   # d(a*b)/da = b
            other.grad += self.data * out.grad   # d(a*b)/db = a
        out._backward = _backward
        return out

    def backward(self):
        # build topological order, then apply chain rule backward
        topo, visited = [], set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)
        build(self)
        self.grad = 1.0                    # d(output)/d(output) = 1
        for v in reversed(topo):
            v._backward()
```

Now differentiate `f = x·y + x` automatically:

```python
x = Value(3.0)
y = Value(4.0)
f = x * y + x
f.backward()

print("f =", f.data)         # value
print("df/dx =", x.grad)     # gradient w.r.t. x
print("df/dy =", y.grad)     # gradient w.r.t. y
```

Output:

```text
f = 15.0
df/dx = 5.0
df/dy = 3.0
```

Verify by hand: `f = xy + x`, so `∂f/∂x = y + 1 = 5` and `∂f/∂y = x = 3`. The engine got both **exactly** — no formulas typed, no approximation. It recorded the operations as a graph, then walked backward applying each operation's local derivative via the chain rule. This is precisely what `loss.backward()` does in PyTorch, just scaled to tensors and many more operations.

---

## How real frameworks scale this up

**PyTorch** and **JAX** are industrial versions of this idea:

- Operate on **tensors** (arrays), not scalars, dispatching to [BLAS](blas-lapack.md)/GPU.
- Support dozens of operations (matmul, conv, activations), each with a defined backward.
- Run on GPUs for massive parallelism.
- JAX uses a functional approach (`grad(f)` transforms a function into its gradient).

```python
import torch                      # pip install torch
x = torch.tensor(3.0, requires_grad=True)
y = torch.tensor(4.0, requires_grad=True)
f = x * y + x
f.backward()
print(x.grad, y.grad)            # tensor(5.), tensor(3.) — same result!
```

!!! note "PyTorch snippet follows documented API"
    PyTorch isn't installed here (our from-scratch engine **is** run-verified). Notice PyTorch gives the *identical* gradients (5 and 3) — because it's doing exactly what our 30-line engine does, just faster and on tensors. Building the toy version is the best way to demystify "backprop."

---

## Practice exercises

1. Add a `__pow__` (power) operation with its derivative (`d(x^n)/dx = n·x^(n-1)`).
2. Add a ReLU activation (`max(0, x)`) with its gradient (1 if x>0 else 0) — the workhorse of neural nets.
3. Build a tiny 1-neuron model and use gradient descent (from [Numerical Optimization](numerical-optimization.md)) to fit it.
4. Explain why reverse mode is preferred over forward mode for training neural networks.
5. Compare your engine's gradients to numerical differentiation `(f(x+h)-f(x))/h` and note the precision difference.
