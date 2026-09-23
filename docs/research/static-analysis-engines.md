---
title: "Static Analysis Engines"
description: Analyze code without running it — AST walking, control flow and data flow
---

# Static Analysis Engines <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research & Compilers</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../core/advanced/ast-manipulation/">AST Manipulation</a>, <a href="../core/advanced/bytecode/">Bytecode</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What static analysis is and why it matters
- [x] Walk the AST to find issues
- [x] Detect unused imports and count definitions
- [x] The idea of control-flow and data-flow analysis
- [x] The tools built on these ideas (flake8, mypy, ruff)

---

## Analysis without execution

**Static analysis** examines source code *without running it* — the opposite of testing, which runs code to observe behavior. It's how linters catch bugs, type checkers verify correctness, and security scanners find vulnerabilities, all before a single line executes. Python makes this unusually accessible because the standard library ships a full parser: the `ast` module turns source into a tree you can inspect.

```
   source code  ──ast.parse──▶  AST (tree)  ──walk/analyze──▶  findings
   "import os"                   Import node                    "unused import"
```

Every Python linter and type checker is, at its core, a program that parses your code into an AST and walks it looking for patterns.

---

## Walking the AST

`ast.walk` yields every node in the tree. Here's a real analysis — finding **unused imports** by comparing imported names against used names. Fully runnable:

```python
import ast

source = '''
import os
import sys

def greet(name):
    print(sys.argv)
    return "hi " + name
'''

tree = ast.parse(source)

# Collect imported top-level names
imported = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            imported.add(alias.asname or alias.name.split(".")[0])

# Collect every name referenced anywhere
used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}

unused = sorted(imported - used)
print("imported:", sorted(imported))
print("used:", sorted(used))
print("unused imports:", unused)
```

Output:

```text
imported: ['os', 'sys']
used: ['name', 'print', 'sys']
unused imports: ['os']
```

The analyzer correctly flags `os` as unused (`sys` is referenced via `sys.argv`, `os` never is) — **without running the code**. This is exactly what `flake8`'s `F401` "imported but unused" check does, in miniature. The whole technique is: parse → walk → compare sets of facts.

Counting definitions is just as direct:

```python
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
print("functions:", funcs)   # -> ['greet']
```

---

## Control flow and data flow

Real analysis engines go deeper than node-counting, building two graphs:

- **Control-Flow Graph (CFG)** — models the possible execution paths (branches, loops, returns). It answers "can this line ever be reached?" (dead-code detection) and "does every path return a value?"
- **Data-Flow Analysis** — tracks how values move through the program. It answers "is this variable used before assignment?", "is this assignment ever read?" (dead store), and powers type inference.

```
   def f(x):              CFG:   [entry]
       if x > 0:                    │
           y = 1                 [x > 0?]
       print(y)   # y may       ╱      ╲
                  # be unbound  [y=1]   (skip)
                                  ╲      ╱
                                  [print(y)]  ← data-flow: is y always defined here? NO
```

Data-flow analysis on this CFG would flag that `y` might be used before assignment — a real bug a simple AST walk misses, because it requires reasoning about *paths*, not just *nodes*.

---

## From AST to a real rule

A minimal linter rule is a function that walks the tree and yields findings:

```python
import ast

def check_bare_except(source: str) -> list[str]:
    """Flag `except:` with no exception type (catches everything, hides bugs)."""
    findings = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(f"line {node.lineno}: bare 'except:' — specify an exception type")
    return findings

code = '''
try:
    risky()
except:
    pass
'''
print(check_bare_except(code))
# -> ["line 4: bare 'except:' — specify an exception type"]
```

This is the entire shape of a linter plugin: match a node pattern, report a location. Scale that to hundreds of rules and you have `flake8` or `pylint`.

!!! note "The example above illustrates the pattern"
    The unused-import and function-count examples are run-verified. The `check_bare_except` snippet follows the same tested `ast.walk` pattern; the line number depends on the exact source layout.

---

## The tools built on this

You rarely write an analysis engine from scratch — you use ones built on exactly these ideas:

| Tool | What it does | Technique |
|---|---|---|
| **flake8 / pyflakes** | Style + logic lint (unused imports, undefined names) | AST walking |
| **pylint** | Deeper lint (design smells, refactoring hints) | AST + inference |
| **mypy / pyright** | Static type checking | AST + data-flow + type inference |
| **ruff** | Extremely fast linter/formatter | AST, written in Rust |
| **bandit** | Security issues | AST pattern matching |

`ruff` is worth calling out — it reimplemented much of this in Rust and is orders of magnitude faster, which is why it's rapidly become the default. But conceptually it does what our examples do: parse, walk, match, report.

---

## Practice exercises

1. Extend the unused-import detector to handle `from x import y` (`ImportFrom` nodes).
2. Write a checker that flags functions longer than N statements (walk `FunctionDef`, count body nodes).
3. Detect `== None` comparisons and suggest `is None` instead (look for `Compare` nodes).
4. Write a rule that finds mutable default arguments (`def f(x=[])`) — a classic Python bug.
5. Explain a bug that requires data-flow analysis (paths) to catch, which a single AST walk cannot.
