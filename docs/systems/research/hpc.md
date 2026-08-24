---
title: HPC Clusters
description: MPI4py, SLURM, Dask, Ray and distributed high-performance computing
---

# HPC Clusters <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: <a href="../proficient/multiprocessing/">Multiprocessing</a>, <a href="../advanced/numba/">Numba</a></span>
  </div>
</div>

---

## MPI4py — Message Passing Interface

MPI is the standard for distributed computing on clusters. Each process (rank) communicates explicitly.

```python
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()    # this process's ID (0, 1, 2, ...)
size = comm.Get_size()    # total number of processes

# ─── Point-to-point communication ─────────────────
if rank == 0:
    data = np.arange(100, dtype=np.float64)
    comm.Send(data, dest=1, tag=0)
    print(f"Rank 0: sent {len(data)} elements")
elif rank == 1:
    data = np.empty(100, dtype=np.float64)
    comm.Recv(data, source=0, tag=0)
    print(f"Rank 1: received, sum = {data.sum()}")

# ─── Collective operations ────────────────────────
# Broadcast (one → all)
if rank == 0:
    data = {"key": "value", "numbers": [1, 2, 3]}
else:
    data = None
data = comm.bcast(data, root=0)   # all ranks now have data

# Scatter (split array across ranks)
if rank == 0:
    big_array = np.arange(1000, dtype=np.float64)
else:
    big_array = None

chunk_size = 1000 // size
local_array = np.empty(chunk_size, dtype=np.float64)
comm.Scatter(big_array, local_array, root=0)

# Each rank processes its chunk
local_sum = local_array.sum()

# Reduce (combine results)
total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
if rank == 0:
    print(f"Total sum: {total_sum}")   # 499500.0

# Gather (collect chunks back)
all_results = comm.gather(local_sum, root=0)
if rank == 0:
    print(f"All partial sums: {all_results}")
```

### Running MPI programs:

```bash
# Run with 4 processes
mpirun -n 4 python my_mpi_script.py

# On a cluster (SLURM)
srun -n 64 python my_mpi_script.py
```

---

## SLURM job scripts

```bash
#!/bin/bash
#SBATCH --job-name=my_python_job
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=16
#SBATCH --time=02:00:00
#SBATCH --partition=compute
#SBATCH --output=output_%j.log
#SBATCH --error=error_%j.log

module load python/3.13
module load openmpi/4.1

# Run with 64 total MPI processes (4 nodes × 16 tasks)
srun python simulation.py --input data.h5 --output results.h5
```

```bash
# Submit job
sbatch job.sh

# Check status
squeue -u $USER

# Cancel job
scancel <job_id>

# Interactive session
salloc --nodes=1 --time=01:00:00
```

---

## Dask — parallel computing in Python

```python
import dask.array as da
import dask.dataframe as dd
from dask.distributed import Client

# Start distributed cluster
client = Client(n_workers=8)   # local, or point to SLURM cluster
print(client.dashboard_link)    # http://localhost:8787/status

# ─── Dask Array (NumPy-like, distributed) ─────────
x = da.random.random((100000, 100000), chunks=(10000, 10000))
# No computation yet! (lazy)

result = (x + x.T).mean(axis=0)
# Still lazy — build computation graph

actual_result = result.compute()   # NOW it executes (distributed)
print(actual_result.shape)          # (100000,)

# ─── Dask DataFrame (Pandas-like, distributed) ────
df = dd.read_csv("s3://bucket/data-*.csv")   # reads many files in parallel
result = df.groupby("category")["amount"].mean().compute()
```

### Dask on SLURM:

```python
from dask_jobqueue import SLURMCluster
from dask.distributed import Client

cluster = SLURMCluster(
    cores=16,
    memory="64GB",
    walltime="02:00:00",
    queue="compute",
)
cluster.scale(jobs=10)   # request 10 SLURM jobs (160 cores total)

client = Client(cluster)
# Now use Dask as normal — work distributed across cluster
```

---

## Ray — distributed computing framework

```python
import ray
import numpy as np

ray.init()   # connect to cluster or start local

# ─── Remote functions ─────────────────────────────
@ray.remote
def compute_chunk(data):
    """Runs on any available node."""
    return np.sum(data ** 2)

# Distribute work
chunks = [np.random.randn(1_000_000) for _ in range(100)]
futures = [compute_chunk.remote(chunk) for chunk in chunks]
results = ray.get(futures)   # collect all results
print(f"Total: {sum(results):.2f}")

# ─── Remote classes (actors) ──────────────────────
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self, n=1):
        self.value += n
        return self.value

    def get(self):
        return self.value

counter = Counter.remote()
ray.get([counter.increment.remote(i) for i in range(100)])
print(ray.get(counter.get.remote()))   # 4950
```

---

## Parallel I/O with HDF5

```python
import h5py
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Parallel HDF5 write
with h5py.File("output.h5", "w", driver="mpio", comm=comm) as f:
    dataset = f.create_dataset("data", (size * 1000, 100), dtype="f8")
    # Each rank writes its chunk
    start = rank * 1000
    end = start + 1000
    dataset[start:end, :] = np.random.randn(1000, 100)

# Parallel HDF5 read
with h5py.File("output.h5", "r", driver="mpio", comm=comm) as f:
    local_data = f["data"][rank*1000:(rank+1)*1000, :]
    local_mean = local_data.mean()

global_mean = comm.reduce(local_mean, op=MPI.SUM, root=0)
if rank == 0:
    print(f"Global mean: {global_mean / size:.6f}")
```

---

## Performance considerations

| Factor | Recommendation |
|---|---|
| Communication overhead | Minimize MPI calls, send large messages |
| Load balancing | Dynamic scheduling for uneven workloads |
| Memory per node | Profile memory, use memory-mapped arrays |
| I/O bottleneck | Use parallel HDF5, minimize filesystem access |
| Scaling efficiency | Measure weak and strong scaling |

---

## Practice Exercises

1. **Implement parallel matrix multiply** with MPI — scatter rows, compute, gather result.
2. **Write a SLURM job script** for a multi-node Python computation.
3. **Use Dask** to process a 100GB CSV dataset that doesn't fit in memory.
4. **Build a Ray pipeline** that distributes image processing across a cluster.
5. **Measure scaling efficiency** — run with 1, 2, 4, 8, 16 processes and plot speedup.
6. **Implement parallel I/O** — each MPI rank writes its data to a shared HDF5 file.
