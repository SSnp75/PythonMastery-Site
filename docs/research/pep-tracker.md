---
title: PEP Tracker
description: Active Python Enhancement Proposals, upcoming features and CPython roadmap
---

# PEP Tracker <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Ongoing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Ongoing</span>
  </div>
</div>

---

## Notable PEPs by Python version

### Python 3.13 (2024)

| PEP | Title | Impact |
|---|---|---|
| 703 | Making the GIL Optional (free-threading) | Experimental `python3.13t` build without GIL |
| 744 | JIT Compilation | Experimental copy-and-patch JIT compiler |
| 702 | Marking deprecations with `warnings.deprecated` | New `@deprecated` decorator |
| 709 | Inlined comprehensions | List/dict/set comps no longer create a nested scope |
| 688 | Buffer Protocol accessible in Python | `collections.abc.Buffer` |

### Python 3.12 (2023)

| PEP | Title | Impact |
|---|---|---|
| 695 | Type Parameter Syntax (`type X = ...`) | `def f[T](x: T) -> T` syntax |
| 684 | Per-interpreter GIL | Each sub-interpreter has its own GIL |
| 701 | Syntactic formalization of f-strings | f-strings can contain any expression |
| 669 | Low impact monitoring (sys.monitoring) | Fast event hooks for debuggers/profilers |
| 688 | Making the buffer protocol accessible | `collections.abc.Buffer` type |

### Python 3.11 (2022)

| PEP | Title | Impact |
|---|---|---|
| 657 | Fine-grained error locations | Error messages point to exact expression |
| 654 | Exception Groups (`ExceptionGroup`) | `try/except*` syntax |
| 673 | `Self` type | `from typing import Self` |
| 681 | `@dataclass_transform` | Type checker support for ORM-like patterns |
| — | Faster CPython | 10-60% faster execution overall |

### Python 3.10 (2021)

| PEP | Title | Impact |
|---|---|---|
| 634 | Structural Pattern Matching | `match/case` statement |
| 604 | `X \| Y` union syntax | Replace `Union[X, Y]` with `X \| Y` |
| 612 | `ParamSpec` | Type decorators properly |
| 618 | `zip(strict=True)` | Error on unequal lengths |

---

## Currently active/draft PEPs (2026)

| PEP | Title | Status |
|---|---|---|
| 703 | Free-threading (no-GIL) | Accepted, maturing |
| 744 | JIT | Experimental, improving |
| 750 | Template Strings | Draft |
| 755 | Implicit string concatenation deprecation | Draft |
| — | Pattern matching enhancements | Discussion |
| — | Lazy imports | Discussion |

---

## How PEPs work

```
Idea → python-ideas discussion → PEP draft → SC review → Accepted/Rejected
                                     ↓
                              Implementation
                                     ↓
                              Merged to CPython main
                                     ↓
                              Released in next Python version
```

### PEP types

| Type | Purpose |
|---|---|
| **Standards Track** | New feature or behavior |
| **Informational** | Design issue or general guidelines |
| **Process** | How the Python community works |

---

## How to read a PEP

Key sections in every PEP:

1. **Abstract** — one paragraph summary
2. **Motivation** — why this change is needed
3. **Rationale** — why this design over alternatives
4. **Specification** — the exact proposal
5. **Backwards Compatibility** — what breaks
6. **Security Implications** — if any
7. **Reference Implementation** — working code (usually a CPython PR)
8. **Rejected Ideas** — alternatives that were considered and why they were rejected

---

## Following CPython development

| Resource | URL |
|---|---|
| PEP index | [peps.python.org](https://peps.python.org) |
| CPython repo | [github.com/python/cpython](https://github.com/python/cpython) |
| Discourse | [discuss.python.org](https://discuss.python.org) |
| Release schedule | [PEP 719](https://peps.python.org/pep-0719/) (3.13 schedule) |
| What's New | [docs.python.org/3/whatsnew](https://docs.python.org/3/whatsnew/) |
| Faster CPython | [github.com/faster-cpython](https://github.com/faster-cpython) |

---

## Practice Exercises

1. **Read PEP 703** (free-threading) and summarize the approach in your own words.
2. **Try free-threading** — build CPython 3.13t and test multi-threaded performance.
3. **Read PEP 634** (pattern matching) and use it in a real project.
4. **Track a PEP** from draft to acceptance — follow the discussion on Discourse.
5. **Write a "mini-PEP"** for a feature you'd like to see in Python.
6. **Build CPython from source** and experiment with the JIT flag.
