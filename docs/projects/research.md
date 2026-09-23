---
title: "Research Projects"
description: Frontier experiments — JITs, interpreters, novel runtimes and language engineering
---

# Research Projects <span class="pm-badge pm-badge-research">Level 7</span>

<div class="pm-topic-header">
  <strong>🛠️ Projects</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Weeks to months each</span>
    <span>📚 Prereqs: <a href="../core/advanced/bytecode.md">Bytecode</a>, <a href="../core/advanced/cpython-internals.md">CPython Internals</a>, <a href="../research/peg-parser.md">PEG Parsers</a></span>
  </div>
</div>

---

These are open-ended, frontier projects — the kind with no known "right answer," only experiments and findings. They exercise the Research & Compilers material and take you to the edge of what Python can do.

!!! note "Different by nature"
    Unlike earlier levels, these have no tidy spec with a finish line. Success is *learning something* and producing an experiment or writeup, not shipping a product. Scope hard, expect dead ends, and document what you discover.

---

## 1. Build a bytecode interpreter (a mini Python VM)

**Goal:** write a stack machine that executes a small subset of Python bytecode.

- **Skills:** [Bytecode](../core/advanced/bytecode.md), stack machines, the `dis` module, opcode semantics.
- **Minimal version:** interpret a handful of opcodes (LOAD_CONST, BINARY_OP, RETURN_VALUE) for arithmetic.
- **Stretch:** functions, loops, more opcodes, a REPL. See [Building a Python VM](../research/python-vm.md). The best way to *truly* understand how Python runs.

## 2. A tiny JIT compiler

**Goal:** compile a hot function to faster code at runtime.

- **Skills:** tracing/profiling, code generation, guards, [Custom JIT Compilers](../research/jit.md).
- **Minimal version:** detect a hot loop and specialize it (even in pure Python, as a concept).
- **Stretch:** emit machine code (via `llvmlite`) or specialized bytecode; deoptimization guards. Deep, hard, and enormously educational.

## 3. A transpiler (Python subset → another language)

**Goal:** translate a subset of Python into C, Rust, or JavaScript.

- **Skills:** [AST Manipulation](../core/advanced/ast-manipulation.md), code generation, semantic mapping, [Transpilers](../research/transpilers.md).
- **Minimal version:** transpile arithmetic + functions to C.
- **Stretch:** more constructs, a runtime shim, actually compile and run the output. Confronts you with the semantic gaps between languages.

## 4. A bytecode rewriter / instrumenter

**Goal:** transform bytecode to add behavior (tracing, coverage, profiling) without changing source.

- **Skills:** [Bytecode Rewriting](../research/bytecode-rewriting.md), `dis`, code objects, import hooks.
- **Minimal version:** rewrite a function's bytecode to log each call.
- **Stretch:** a coverage tool, an auto-instrumentation library, import-time rewriting. This is how tools like coverage.py and some profilers work.

## 5. A custom static analysis tool

**Goal:** analyze code for a specific class of bug or pattern nobody else checks.

- **Skills:** [Static Analysis Engines](../research/static-analysis-engines.md), AST walking, control/data flow.
- **Minimal version:** a linter rule that catches one real anti-pattern (uses the tested AST examples).
- **Stretch:** control-flow graphs, data-flow analysis, a `flake8` plugin, type inference. Genuinely useful *and* research-grade.

## 6. A domain-specific language (DSL)

**Goal:** design and implement a small language for a specific domain.

- **Skills:** lexing, parsing (recursive descent / PEG — see [PEG Parser Internals](../research/peg-parser.md)), evaluation.
- **Minimal version:** an expression language with an evaluator (the tested parser in [Grammar Modification](../research/grammar-modification.md) is a starting point).
- **Stretch:** variables, functions, control flow; compile it to Python or bytecode. Language design from scratch.

---

## How to approach research projects

```
   1. Pick a narrow, concrete question ("can I interpret these 5 opcodes?").
   2. Build the smallest thing that answers it.
   3. Write down what you learned — the findings ARE the deliverable.
   4. Expand only if the question is still interesting.
```

- **Read the papers** (see [Research Papers](../emerging/research-papers.md)) — someone has likely explored nearby territory.
- **Expect to be stuck** — that's the job at this level. Dead ends are data.
- **Share findings** — a blog post or repo writeup is the natural output, more than a "finished product."

!!! tip "The site itself is an example"
    Several pages here (the [Raft](../distributed/raft.md), [CRDT](../distributed/crdts.md), and parser examples) are exactly this kind of work: take a hard concept, implement its core in small tested Python, and explain it. That's a research project in miniature — and a great template for your own.
