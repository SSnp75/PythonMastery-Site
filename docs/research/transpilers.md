---
title: Transpilers
description: Source-to-source compilation — AST parsing, code generation, and a working Python-to-C expression transpiler
---

# Transpilers <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisite: <a href="../core/advanced/ast-manipulation/">AST Manipulation</a></span>
  </div>
</div>

---

## What is a transpiler?

A source-to-source compiler translates code between languages at the **same** abstraction
level (unlike a compiler, which lowers to machine code).

```
Python source → tokenize → parse (AST) → transform → generate target source
```

---

## Existing Python transpilers

| Tool | Target | Notes |
|---|---|---|
| **Cython** | C | superset of Python, compiled extension |
| **mypyc** | C | compiles type-annotated Python |
| **Transcrypt** | JavaScript | runs Python in the browser |
| **Codon** | native (LLVM) | high-performance, static subset |
| **py2many** | C++/Rust/Go/... | experimental multi-target |

---

## Reading the AST

The standard library parses Python into an AST you can walk — the front half of any
transpiler:

```python
import ast

tree = ast.parse("x = 1 + 2 * 3")
print(ast.dump(tree, indent=None)[:60])
# Module(body=[Assign(targets=[Name(id='x', ctx=Store())
```

`ast.unparse` turns an AST back into source — a trivial Python→Python transpiler:

```python
import ast

tree = ast.parse("a=1+2")
print(ast.unparse(tree))   # a = 1 + 2
```

---

## A working Python-to-C expression transpiler

This walks an arithmetic expression's AST and emits equivalent C. It handles numbers,
names, and the four basic operators:

```python
import ast

def to_c(node):
    if isinstance(node, ast.Expression):
        return to_c(node.body)
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.BinOp):
        op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}[type(node.op)]
        return f"({to_c(node.left)} {op} {to_c(node.right)})"
    raise NotImplementedError(type(node).__name__)

tree = ast.parse("a + 2 * b", mode="eval")
print(to_c(tree))   # (a + (2 * b))
```

The output is valid C for the same expression. A real transpiler extends this to
statements, control flow, and type inference — but the shape is always *parse → walk → emit*.

---

## The hard parts

- **Dynamic typing** — the target may need inferred or declared types.
- **Runtime semantics** — duck typing, exceptions, and the GC rarely map 1:1.
- **Standard library** — every used function must have a target equivalent.

---

## Practice exercises

1. Extend `to_c` to support unary minus (`ast.UnaryOp`).
2. Add comparison operators (`<`, `>`, `==`) to the transpiler.
3. Write a transpiler that emits JavaScript instead of C from the same AST.
4. Use `ast.NodeVisitor` to collect every variable name referenced in an expression.
