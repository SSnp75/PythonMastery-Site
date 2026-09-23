---
title: "Grammar Modification"
description: Add new syntax to Python — grammar files, parser generation and the tradeoffs
---

# Grammar Modification <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research & Compilers</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="peg-parser/">PEG Parser Internals</a>, <a href="../core/advanced/ast-manipulation/">AST Manipulation</a></span>
  </div>
</div>

---

## What you'll learn

- [x] How Python's grammar becomes a parser
- [x] Build a tiny parser to understand the pipeline
- [x] What "modifying the grammar" actually involves
- [x] Realistic alternatives that don't fork Python
- [x] Why new syntax is rarely the right answer

---

## From grammar to parser

Every language is defined by a **grammar** — formal rules describing valid syntax. Python's grammar lives in `Grammar/python.gram` in the CPython source, written in **PEG** (Parsing Expression Grammar) form since Python 3.9. At build time, a parser generator turns that grammar file into the C parser that reads your `.py` files.

```
   Grammar/python.gram  ──generator──▶  C parser  ──parses──▶  AST  ──compiles──▶  bytecode
   (the rules)                          (the code)
```

"Modifying the grammar" means editing those rules and rebuilding CPython — a genuine fork of the language. Before we get there, let's build a tiny parser so the pipeline is concrete.

## A recursive-descent parser you can run

You can understand grammars by implementing one. Here's a parser+evaluator for a small expression grammar — fully runnable:

```python
import re

# grammar:  expr := term (('+' | '-') term)*
#           term := NUMBER
def tokenize(s: str) -> list[str]:
    return re.findall(r'\d+|[+\-]', s.replace(" ", ""))

def evaluate(s: str) -> int:
    toks = tokenize(s)
    pos = 0
    def term() -> int:
        nonlocal pos
        v = int(toks[pos]); pos += 1
        return v
    def expr() -> int:
        nonlocal pos
        v = term()
        while pos < len(toks) and toks[pos] in "+-":
            op = toks[pos]; pos += 1
            rhs = term()
            v = v + rhs if op == "+" else v - rhs
        return v
    return expr()

print(evaluate("1 + 2 + 3"))     # -> 6
print(evaluate("10 - 3 + 1"))    # -> 8
```

Output:

```text
6
8
```

Each grammar rule (`expr`, `term`) became a function; the structure of the code mirrors the structure of the grammar. This is **recursive descent**, the same style CPython's PEG parser uses (generated automatically rather than hand-written). Adding a rule for `*` and `/` would mean adding a `factor` function — that's what "extending a grammar" feels like in the small.

---

## Modifying Python's actual grammar

To add real syntax to Python (say, a new operator or keyword), the steps are:

1. **Edit `Grammar/python.gram`** — add or change a PEG rule.
2. **Regenerate the parser** — run CPython's build, which invokes the parser generator (`pegen`).
3. **Update the AST** — new syntax usually needs new AST node types (`Grammar/Python.asdl`).
4. **Update the compiler** — teach `compile.c` how to turn the new AST nodes into bytecode.
5. **Rebuild CPython** — you now have a forked interpreter that understands your syntax.

!!! warning "This forks the language"
    A modified grammar produces a Python that only *your* build understands. Code using the new syntax won't run on standard CPython, breaks every tool (linters, formatters, IDEs, type checkers), and can't be shared. It's a research/experimentation activity, not a way to ship features. See [Interpreter Forking](interpreter-forking.md) for the broader picture.

---

## Realistic alternatives (no fork needed)

Almost always, you want new *behavior*, not new *syntax* — and Python gives you powerful ways to get it without touching the grammar:

- **AST transformation at import time** — use an import hook to rewrite the AST of modules as they load (see [AST Manipulation](../core/advanced/ast-manipulation.md) and [Import System](../core/advanced/import-system.md)). This lets you change *semantics* while keeping valid Python syntax. Libraries like `pytest` (assertion rewriting) and `MacroPy` did exactly this.
- **Operator overloading & dunder methods** — a huge amount of "custom syntax" is really just `__add__`, `__matmul__`, `__getitem__`, context managers, and decorators. The `@` operator was added to the language specifically so libraries like NumPy could express matrix multiply without a fork.
- **A DSL parsed at runtime** — parse your custom mini-language from strings (like the expression evaluator above), rather than embedding it in Python's grammar.

!!! tip "Reach for AST rewriting, not a grammar fork"
    If you think you need new syntax, you almost certainly want an import-time AST transform or clever use of existing operators. Those stay compatible with real Python and its tooling. A grammar fork is a last resort for language *research*.

---

## Practice exercises

1. Extend the expression evaluator with `*` and `/` at correct precedence (add a `factor` rule/function).
2. Add parentheses support: `factor := NUMBER | '(' expr ')'`.
3. Explain, step by step, what breaks in your toolchain if you add a new keyword by forking the grammar.
4. Research how `pytest` rewrites `assert` statements via an import hook — and why that needed no grammar change.
5. Describe a feature you might *think* needs new syntax, and design it instead with operator overloading or a decorator.
