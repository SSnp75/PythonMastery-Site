---
title: Distributed Training
description: DDP, FSDP, model sharding, pipeline parallelism and multi-GPU strategies
---

# Distributed Training <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: PyTorch basics, <a href="../../systems/proficient/multiprocessing/">Multiprocessing</a></span>
  </div>
</div>

---

## Why distribute training?

| Scenario | Solution |
|---|---|
| Data doesn't fit in GPU memory | Gradient accumulation, data parallelism |
| Model doesn't fit on one GPU | Model parallelism, FSDP |
| Training takes too long | Data parallelism across multiple GPUs |
| Model + optimizer state too large | ZeRO / FSDP sharding |

---

## Data Parallelism (DDP)

The simplest form: same model on each GPU, different data batches, synchronized gradients.

```python
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import os

def setup(rank, world_size):
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)

    # Model on this GPU
    model = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10),
    ).to(rank)
    model = DDP(model, device_ids=[rank])

    # Distributed sampler ensures each GPU gets different data
    dataset = load_dataset()
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=64, sampler=sampler)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(10):
        sampler.set_epoch(epoch)   # shuffle differently each epoch
        for x, y in dataloader:
            x, y = x.to(rank), y.to(rank)
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()     # gradients auto-synchronized by DDP!
            optimizer.step()

        if rank == 0:
            print(f"Epoch {epoch}: loss={loss.item():.4f}")

    cleanup()

# Launch
import torch.multiprocessing as mp
world_size = torch.cuda.device_count()
mp.spawn(train, args=(world_size,), nprocs=world_size)
```

### How DDP works internally:

```
GPU 0: forward → loss → backward → [all-reduce gradients] → optimizer.step()
GPU 1: forward → loss → backward → [all-reduce gradients] → optimizer.step()
GPU 2: forward → loss → backward → [all-reduce gradients] → optimizer.step()

All GPUs end up with identical model parameters after each step.
```

---

## FSDP (Fully Sharded Data Parallel)

For models too large for one GPU — shards model parameters, gradients AND optimizer states:

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy

def train_fsdp(rank, world_size):
    setup(rank, world_size)

    model = LargeModel().to(rank)

    # Wrap with FSDP — parameters are sharded across GPUs
    model = FSDP(
        model,
        sharding_strategy=ShardingStrategy.FULL_SHARD,
        device_id=rank,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    for batch in dataloader:
        optimizer.zero_grad()
        output = model(batch["input_ids"].to(rank))
        loss = output.loss
        loss.backward()
        optimizer.step()

    cleanup()
```

### FSDP memory savings:

```
Model: 7B parameters (28 GB in fp32)
Optimizer (Adam): 2x model = 56 GB
Gradients: 28 GB
Total per GPU without FSDP: 112 GB (impossible on 80GB A100!)

With FSDP (8 GPUs): 112 / 8 = 14 GB per GPU ✓
```

---

## Gradient accumulation (simulating larger batches)

```python
accumulation_steps = 4   # effective batch = 4 * batch_size

optimizer.zero_grad()
for i, (x, y) in enumerate(dataloader):
    output = model(x)
    loss = criterion(output, y) / accumulation_steps   # normalize
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

---

## Mixed precision training

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for x, y in dataloader:
    optimizer.zero_grad()

    # Forward pass in float16 (2x faster, half memory)
    with autocast():
        output = model(x.to(device))
        loss = criterion(output, y.to(device))

    # Backward with scaled gradients (avoid underflow in fp16)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

---

## Pipeline parallelism

Split model layers across GPUs — micro-batches flow through the pipeline:

```python
# GPipe-style pipeline
# GPU 0: layers 0-11
# GPU 1: layers 12-23
# GPU 2: layers 24-35
# GPU 3: layers 36-47

# While GPU 0 processes micro-batch 2,
# GPU 1 processes micro-batch 1 (from GPU 0's output)
# → Reduces idle time (bubble)
```

---

## Checkpointing large models

```python
import torch.distributed.checkpoint as dcp
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import StateDictType

# Save (each rank saves its shard)
with FSDP.state_dict_type(model, StateDictType.SHARDED_STATE_DICT):
    state = {"model": model.state_dict(), "optimizer": optimizer.state_dict()}
    dcp.save(state, checkpoint_id="checkpoints/epoch_5")

# Load
with FSDP.state_dict_type(model, StateDictType.SHARDED_STATE_DICT):
    state = {"model": model.state_dict(), "optimizer": optimizer.state_dict()}
    dcp.load(state, checkpoint_id="checkpoints/epoch_5")
    model.load_state_dict(state["model"])
    optimizer.load_state_dict(state["optimizer"])
```

---

## Launch scripts

```bash
# torchrun (recommended)
torchrun --nproc_per_node=4 train.py

# Multi-node
torchrun --nproc_per_node=4 --nnodes=2 --node_rank=0 \
         --master_addr=192.168.1.1 --master_port=12355 train.py
```

---

## Practice Exercises

1. **Convert a single-GPU training script** to use DDP with 2+ GPUs.
2. **Implement gradient accumulation** and verify it matches a larger batch size.
3. **Use mixed precision** and measure the speedup and memory savings.
4. **Wrap a model with FSDP** and verify memory is sharded across GPUs.
5. **Implement checkpointing** that saves/resumes training across crashes.
6. **Benchmark** DDP scaling: 1 GPU vs 2 vs 4 — measure throughput (samples/sec).
