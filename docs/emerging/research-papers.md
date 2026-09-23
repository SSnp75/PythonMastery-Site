---
title: "Research Papers"
description: Foundational and current papers worth reading on Python internals, JITs, distributed systems and ML
---

# Research Papers <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🚀 Emerging & Evolving Python</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Ongoing</span>
    <span>📚 For the deep end</span>
  </div>
</div>

---

## What you'll learn

- [x] Why reading papers is worth it
- [x] Foundational papers behind the concepts on this site
- [x] How to read a technical paper efficiently
- [x] Where to find and track research

!!! note "This is a curated reading guide"
    This page points to influential work rather than reproducing it. Paper titles and authors are given so you can find the originals; always read from the primary source.

---

## Why read papers?

Most engineering knowledge is second-hand — blog posts summarizing summaries. Papers are the **primary source**: the actual ideas, with their precise claims and honest limitations. For the deep topics on this site (consensus, JITs, CRDTs, ML systems), reading the original paper gives an understanding that tutorials can't. You don't need a PhD — you need patience and a method (below).

---

## Foundational papers by topic

**Distributed systems** (see the Distributed Systems section)
- *In Search of an Understandable Consensus Algorithm* (Ongaro & Ousterhout, 2014) — the **Raft** paper. Unusually readable; the best entry point to consensus.
- *The Part-Time Parliament* / *Paxos Made Simple* (Lamport) — **Paxos**. Famously dense; read Raft first.
- *Dynamo: Amazon's Highly Available Key-value Store* (2007) — eventual consistency, consistent hashing, and the ideas behind **CRDTs** in practice.
- *A Comprehensive Study of Convergent and Commutative Replicated Data Types* (Shapiro et al.) — the **CRDT** foundations.
- *Time, Clocks, and the Ordering of Events in a Distributed System* (Lamport, 1978) — logical/vector clocks; one of the most cited CS papers ever.

**Language runtimes & JITs** (see Research & Performance sections)
- *The Implementation of Lua 5.0* — a beautifully clear paper on implementing a dynamic language.
- Papers on **tracing JITs** (PyPy's meta-tracing work) — how dynamic languages get fast.
- The **LLVM** paper (Lattner & Adve) — the compiler infrastructure behind Numba and much else.

**Machine learning systems** (see Data & AI section)
- *Attention Is All You Need* (Vaswani et al., 2017) — the **Transformer**; underpins modern LLMs.
- *ImageNet Classification with Deep CNNs* (AlexNet, 2012) — kicked off the deep-learning era.
- Papers on **distributed training** (data/model parallelism) and systems like TensorFlow/JAX.

**Databases & storage**
- *The Google File System* and *MapReduce* — foundational big-data systems.
- *Bigtable*, *Spanner* — Google's storage systems (Spanner uses Paxos).

---

## How to read a paper efficiently

Don't read linearly front-to-back the first time. A widely-used three-pass method:

```
   Pass 1 (~10 min):  Title, abstract, intro, section headings, conclusion.
                      → What problem? What's the claim? Worth continuing?
   Pass 2 (~1 hr):    Read the body, look at figures, skip heavy proofs.
                      → Understand the approach and evidence.
   Pass 3 (deep):     Re-implement or verify the key idea; scrutinize proofs.
                      → Only for papers you truly need to master.
```

Most papers only need pass 1 or 2. Reserve pass 3 for the few that matter to your work. Reading the abstract + conclusion first tells you quickly whether to invest more.

!!! tip "Implement to understand"
    The deepest understanding comes from building the idea. Much of this site's content did exactly that — the [Raft](../distributed/raft.md), [CRDT](../distributed/crdts.md), and [saga](../distributed/saga.md) pages implement the papers' core ideas in small, tested Python. Reading + reimplementing beats reading alone.

---

## Where to find and track research

- **arXiv.org** — free preprints (cs.DC for distributed, cs.PL for languages, cs.LG for ML).
- **Papers We Love** (paperswelove.org) — a curated community collection of great CS papers.
- **Google Scholar** — search and follow citations; "cited by" reveals follow-up work.
- **Conference proceedings** — OSDI, SOSP (systems), PLDI, POPL (languages), NeurIPS, ICML (ML).
- **The morning paper** (archived) — accessible summaries that point to originals.

---

## Practice exercises

1. Do a pass-1 read of the Raft paper (10 min) and write the problem + main claim in two sentences.
2. Compare the Raft paper to this site's [Raft page](../distributed/raft.md) — what did the page simplify?
3. Pick a paper behind a tool you use (LLVM, Transformer) and do a pass-2 read.
4. Find a paper on arXiv in an area you care about and apply the three-pass method.
5. Reimplement one small idea from a paper in Python and test it (as this site does).
