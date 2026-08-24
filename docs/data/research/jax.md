---
title: JAX Internals
description: XLA compilation, jit, grad, vmap, pytrees and functional transformations
---

# JAX Internals <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: <a href="../intermediate/numpy/">NumPy</a>, Calculus</span>
  </div>
</div>

---

## What is JAX?

JAX = **NumPy + Autograd + XLA**. Write NumPy-like code that:

- Compiles to XLA (runs on CPU/GPU/TPU)
- Has automatic differentiation (forward and reverse mode)
- Vectorizes with `vmap`
- Parallelizes with `pmap`

```python
import jax
import jax.numpy as jnp

# Looks like NumPy, runs on GPU
x = jnp.array([1.0, 2.0, 3.0])
y = jnp.sin(x) ** 2 + jnp.cos(x)
print(y)   # [1.382, 0.494, 0.01]  (on GPU if available)
```

---

## `jax.jit` — Just-In-Time compilation

```python
import jax
import jax.numpy as jnp

def slow_function(x):
    """Without JIT — each operation is a separate kernel launch."""
    return jnp.sum(jnp.sin(x) ** 2 + jnp.cos(x) ** 2)

# With JIT — entire function compiled to one XLA program
@jax.jit
def fast_function(x):
    return jnp.sum(jnp.sin(x) ** 2 + jnp.cos(x) ** 2)

x = jnp.ones(10_000_000)

# First call compiles (slow), subsequent calls are fast
result = fast_function(x)   # ~0.001s after compilation
# result = n (sin²x + cos²x = 1, so sum = n)

# Timing comparison
import time

# Warm up JIT
fast_function(x).block_until_ready()

start = time.time()
for _ in range(100):
    slow_function(x).block_until_ready()
print(f"No JIT: {time.time() - start:.4f}s")

start = time.time()
for _ in range(100):
    fast_function(x).block_until_ready()
print(f"With JIT: {time.time() - start:.4f}s")  # 10-100x faster
```

### JIT tracing and static shapes

```python
# JIT traces with abstract shapes — concrete values become static
@jax.jit
def f(x, n):
    return x[:n]   # ERROR! n must be known at trace time

# Solution: mark as static
from functools import partial

@partial(jax.jit, static_argnums=(1,))
def f(x, n):
    return x[:n]   # OK — n is treated as compile-time constant

print(f(jnp.arange(10), 5))   # [0, 1, 2, 3, 4]
```

---

## `jax.grad` — automatic differentiation

```python
import jax
import jax.numpy as jnp

# Scalar function
def f(x):
    return jnp.sin(x) ** 2

# First derivative
df = jax.grad(f)
print(df(jnp.pi / 4))   # 2 * sin(π/4) * cos(π/4) = 1.0

# Second derivative
ddf = jax.grad(jax.grad(f))
print(ddf(jnp.pi / 4))  # 2(cos²x - sin²x) at π/4 = 0.0

# Gradient of a loss function
def mse_loss(params, x, y):
    predictions = params["w"] * x + params["b"]
    return jnp.mean((predictions - y) ** 2)

params = {"w": jnp.array(1.0), "b": jnp.array(0.0)}
x = jnp.array([1.0, 2.0, 3.0])
y = jnp.array([2.0, 4.0, 6.0])

grads = jax.grad(mse_loss)(params, x, y)
print(grads["w"])   # gradient w.r.t. weight
print(grads["b"])   # gradient w.r.t. bias
```

### Value and gradient together

```python
loss_val, grads = jax.value_and_grad(mse_loss)(params, x, y)
print(f"Loss: {loss_val:.4f}")
print(f"Grads: w={grads['w']:.4f}, b={grads['b']:.4f}")
```

---

## `jax.vmap` — automatic vectorization

```python
import jax
import jax.numpy as jnp

# Function that works on a single example
def predict_single(params, x):
    return jnp.dot(params, x)

# Vectorize over a batch (no manual batching!)
predict_batch = jax.vmap(predict_single, in_axes=(None, 0))
# in_axes=(None, 0) → don't batch params, batch x along axis 0

params = jnp.array([1.0, 2.0, 3.0])
X = jnp.array([[1.0, 0.0, 0.0],
               [0.0, 1.0, 0.0],
               [0.0, 0.0, 1.0]])

predictions = predict_batch(params, X)
print(predictions)   # [1.0, 2.0, 3.0]

# Combine vmap with grad — per-example gradients!
per_example_grads = jax.vmap(jax.grad(lambda p, x: predict_single(p, x) ** 2), in_axes=(None, 0))
```

---

## Pytrees — JAX's data structures

JAX functions work with **pytrees** — nested containers of arrays:

```python
import jax
import jax.numpy as jnp
from jax import tree_util

# Pytrees can be dicts, lists, tuples, namedtuples, custom classes
params = {
    "linear1": {"w": jnp.ones((3, 4)), "b": jnp.zeros(4)},
    "linear2": {"w": jnp.ones((4, 2)), "b": jnp.zeros(2)},
}

# tree_map applies a function to every leaf
doubled = jax.tree_util.tree_map(lambda x: x * 2, params)

# tree_leaves flattens
leaves = jax.tree_util.tree_leaves(params)
print(f"Total parameters: {sum(x.size for x in leaves)}")   # 3*4 + 4 + 4*2 + 2 = 26

# Use with grad — gradients have same tree structure!
def loss(params, x, y):
    h = jnp.tanh(x @ params["linear1"]["w"] + params["linear1"]["b"])
    out = h @ params["linear2"]["w"] + params["linear2"]["b"]
    return jnp.mean((out - y) ** 2)

grads = jax.grad(loss)(params, jnp.ones((5, 3)), jnp.ones((5, 2)))
# grads has SAME structure as params — dict of dicts of arrays
```

---

## Training loop from scratch

```python
import jax
import jax.numpy as jnp
from jax import random

# Initialize parameters
def init_params(key, layer_sizes):
    params = []
    for i in range(len(layer_sizes) - 1):
        key, subkey = random.split(key)
        w = random.normal(subkey, (layer_sizes[i], layer_sizes[i+1])) * 0.01
        b = jnp.zeros(layer_sizes[i+1])
        params.append({"w": w, "b": b})
    return params

# Forward pass
def forward(params, x):
    for layer in params[:-1]:
        x = jnp.tanh(x @ layer["w"] + layer["b"])
    # Last layer — no activation
    x = x @ params[-1]["w"] + params[-1]["b"]
    return x

# Loss
def loss_fn(params, x, y):
    preds = forward(params, x)
    return jnp.mean((preds - y) ** 2)

# Training step
@jax.jit
def train_step(params, x, y, lr=0.01):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    # SGD update
    params = jax.tree_util.tree_map(lambda p, g: p - lr * g, params, grads)
    return params, loss

# Training loop
key = random.PRNGKey(42)
params = init_params(key, [2, 32, 32, 1])

# Dummy data: y = x1² + x2²
X = random.normal(key, (1000, 2))
Y = jnp.sum(X**2, axis=1, keepdims=True)

for epoch in range(1000):
    params, loss = train_step(params, X, Y)
    if epoch % 100 == 0:
        print(f"Epoch {epoch:4d} | Loss: {loss:.6f}")
```

---

## `pmap` — parallelism across devices

```python
# Distribute computation across multiple GPUs/TPUs
@jax.pmap
def parallel_forward(params, x):
    return forward(params, x)

# Replicate params across devices
n_devices = jax.device_count()
replicated_params = jax.tree_util.tree_map(
    lambda x: jnp.stack([x] * n_devices), params
)
```

---

## Practice Exercises

1. **Implement gradient descent** for linear regression using only `jax.grad` and `jax.jit`.
2. **Build a neural network** (MLP) from scratch with JAX — train on MNIST.
3. **Use `vmap`** to compute per-example gradients efficiently.
4. **Implement Adam optimizer** using pytree operations.
5. **Compare JAX vs NumPy** speed on matrix operations with varying sizes.
6. **Build a custom layer** (attention mechanism) and verify gradients with `jax.grad`.
