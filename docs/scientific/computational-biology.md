---
title: "Computational Biology"
description: Sequence analysis, structural biology and genomics with Python
---

# Computational Biology <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../domains/bioinformatics.md">Python for Bioinformatics</a>, <a href="../algorithms/dynamic-programming.md">Dynamic Programming</a></span>
  </div>
</div>

---

## What you'll learn

- [x] How computational biology relates to bioinformatics
- [x] Sequence alignment via dynamic programming (tested)
- [x] Structural biology concepts
- [x] Genomic-scale data processing
- [x] The scientific tooling

Computational biology applies computation and modeling to biological questions — overlapping with [bioinformatics](../domains/bioinformatics.md) but leaning more toward algorithms, structure, and simulation. The alignment scoring example here is **run-verified**.

---

## Biology as an algorithms problem

Much of computational biology reduces to well-known CS problems:

- **Sequence alignment** → dynamic programming (edit distance).
- **Phylogenetic trees** → graph/tree algorithms.
- **Protein folding** → optimization and simulation.
- **Genome assembly** → graph problems (de Bruijn graphs).

This is why strong CS fundamentals transfer directly. Let's see the most central one.

---

## Sequence alignment scoring (tested)

Comparing two DNA/protein sequences means finding their best alignment — and the core is a **dynamic programming** score, essentially edit distance. Here's the minimum edit distance (Levenshtein) between two sequences, pure Python:

```python
def edit_distance(a: str, b: str) -> int:
    """Minimum single-character edits (insert/delete/substitute) to turn a into b."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                      # delete all of a's first i chars
    for j in range(n + 1):
        dp[0][j] = j                      # insert all of b's first j chars
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,           # deletion
                dp[i][j-1] + 1,           # insertion
                dp[i-1][j-1] + cost,      # match or substitution
            )
    return dp[m][n]

print(edit_distance("GATTACA", "GATGCA"))
print(edit_distance("AAAA", "AAAA"))
```

Output:

```text
2
0
```

`GATTACA` → `GATGCA` needs 2 edits; identical sequences need 0. This dynamic-programming table is the foundation of **Needleman-Wunsch** (global alignment) and **Smith-Waterman** (local alignment) — the algorithms that power sequence comparison across all of biology. Real aligners add gap penalties and substitution scoring matrices (like BLOSUM for proteins), but the DP core is exactly this. See [Dynamic Programming](../algorithms/dynamic-programming.md).

---

## Structural biology

Beyond sequences, computational biology studies 3D structure:

- **Protein structure** — proteins fold into shapes that determine function. Predicting the fold from the sequence was a grand challenge, recently revolutionized by **AlphaFold** (deep learning).
- **Molecular dynamics** — simulating how molecules move and interact over time (continuous simulation — see [Computational Physics](computational-physics.md)); tools like OpenMM.
- **Structure analysis** — measuring distances, angles, and binding sites in 3D coordinates (BioPython's `Bio.PDB`).

---

## Genomic-scale data

Modern genomics processes enormous datasets — a single sequencing run produces billions of bases:

- **Formats** — FASTQ (reads + quality), BAM/SAM (alignments), VCF (variants).
- **Pipelines** — raw reads → quality control → alignment → variant calling → annotation, orchestrated as a [data pipeline](../projects/advanced.md) (Snakemake, Nextflow).
- **Scale** — needs efficient tools (`pysam`), often sparse structures ([Sparse Tensors](sparse-tensors.md)), and sometimes distributed processing.

---

## The ecosystem

| Need | Tool |
|---|---|
| Sequences, files, translation | BioPython |
| Alignment | BLAST, Biopython, minimap2 |
| Structure | Bio.PDB, PyMOL, OpenMM |
| Genomics data | pysam, scikit-bio |
| Numerical / ML | NumPy, scikit-learn, PyTorch |
| Pipelines | Snakemake, Nextflow |

!!! note "Bio libraries follow documented APIs"
    BioPython and genomics tools aren't installed here — the edit-distance alignment core above **is** run-verified. The libraries handle formats, scoring matrices, and scale; the DP algorithm shown is what they compute underneath.

---

## Practice exercises

1. Modify `edit_distance` to also return the aligned strings (traceback through the DP table).
2. Add a gap penalty different from the substitution cost and observe how alignments change.
3. Use edit distance to find the closest match of a short sequence within a longer one.
4. Explain why sequence alignment is a dynamic-programming problem (optimal substructure).
5. Research how AlphaFold changed protein structure prediction, and what problem it solved.
