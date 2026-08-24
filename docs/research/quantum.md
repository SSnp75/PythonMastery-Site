---
title: Quantum Computing
description: Qiskit, quantum circuits, simulation and quantum algorithms
---

# Quantum Computing <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
  </div>
</div>

---

## Qiskit basics

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)              # Hadamard gate
qc.cx(0, 1)          # CNOT — creates entanglement
qc.measure([0, 1], [0, 1])

sim = AerSimulator()
result = sim.run(qc, shots=1000).result()
print(result.get_counts())   # {'00': ~500, '11': ~500}
```

---

<div class="pm-coming-soon">
<h3>📝 More sections coming</h3>
<p>Quantum gates, Grover's algorithm, VQE, quantum error correction, Cirq</p>
</div>
