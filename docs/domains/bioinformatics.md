---
title: "Python for Bioinformatics"
description: Analyze biological sequences and genomic data with Python and BioPython
---

# Python for Bioinformatics <span class="pm-badge pm-badge-proficient">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../core/beginner/data-structures.md">Data Structures</a>, <a href="../core/beginner/file-handling.md">File Handling</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Working with DNA/RNA/protein sequences
- [x] Basic sequence operations (tested, pure Python)
- [x] File formats (FASTA/FASTQ) and BioPython
- [x] Sequence alignment and genomics concepts
- [x] The ecosystem

Bioinformatics applies computation to biology — analyzing DNA, proteins, and genomes. Python is the field's dominant language. The basic sequence operations here are **run-verified** with pure Python; higher-level work uses **BioPython** (documented API).

---

## Sequences are just strings (tested)

DNA is a string over the alphabet `A, C, G, T`. Many core operations are pure string manipulation — runnable:

```python
def gc_content(dna: str) -> float:
    """Fraction of G and C bases — a basic genomic measure."""
    gc = sum(1 for base in dna if base in "GC")
    return gc / len(dna)

def complement(dna: str) -> str:
    """The complementary strand (A<->T, C<->G)."""
    pairs = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(pairs[b] for b in dna)

def reverse_complement(dna: str) -> str:
    return complement(dna)[::-1]

seq = "GATTACA"
print("GC content:", round(gc_content(seq), 3))
print("complement:", complement(seq))
print("reverse complement:", reverse_complement(seq))
```

Output:

```text
GC content: 0.286
complement: CTAATGT
reverse complement: TGTAATC
```

The reverse complement matters biologically — DNA's two strands run in opposite directions, so the reverse complement is what the other strand reads. All of this is `dict` lookups and slicing; the biology is in *interpreting* the results, not the code.

Transcription (DNA → RNA) is just replacing T with U:

```python
def transcribe(dna: str) -> str:
    return dna.replace("T", "U")

print(transcribe("GATTACA"))    # -> GAUUACA
```

---

## FASTA/FASTQ and BioPython

Real sequence data comes in formats like **FASTA** (sequences) and **FASTQ** (sequences + quality scores). **BioPython** parses these and provides the field's toolkit:

```python
from Bio import SeqIO          # pip install biopython
from Bio.Seq import Seq

# Parse a FASTA file
for record in SeqIO.parse("sequences.fasta", "fasta"):
    print(record.id, len(record.seq))
    print(record.seq.reverse_complement())

# BioPython Seq objects know biology
dna = Seq("GATTACA")
protein = dna.translate()      # DNA -> amino acids
```

!!! note "BioPython snippet follows documented API"
    BioPython isn't installed here, so this isn't run-verified (the pure-Python sequence ops above are). BioPython handles the file formats, database access (GenBank), translation tables, and much more — reinventing it by hand is unnecessary.

---

## Bigger concepts

- **Sequence alignment** — finding how two sequences match up (mutations, insertions, deletions). Algorithms like Needleman-Wunsch (global) and Smith-Waterman (local) use dynamic programming (see the Algorithms section). Tools: BioPython, BLAST.
- **Phylogenetics** — building evolutionary trees from sequence similarity.
- **Genomic pipelines** — processing raw sequencer output through alignment, variant calling, and annotation, often orchestrated as a [data pipeline](../projects/advanced.md).

---

## The ecosystem

| Need | Tool |
|---|---|
| Core toolkit | BioPython |
| Numerical | NumPy, Pandas |
| Alignment | BLAST, Biopython pairwise |
| Genomics data | pysam, scikit-bio |
| Pipelines | Snakemake, Nextflow |

---

## Practice exercises

1. Write a function that counts each base (A/C/G/T) in a sequence using `collections.Counter`.
2. Find the most common 3-base codon in a sequence.
3. Implement transcription and a simple codon → amino acid lookup for a few codons.
4. Detect whether a sequence is a palindrome under reverse-complement (a restriction site property).
5. Explain why reverse complement is biologically meaningful, referencing DNA's two strands.
