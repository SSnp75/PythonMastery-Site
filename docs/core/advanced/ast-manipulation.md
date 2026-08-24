---
title: AST Manipulation
description: ast module, NodeVisitor, NodeTransformer, code transformation and static analysis
---

# AST Manipulation <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisite: <a href="bytecode/">Bytecode</a></span>
  </div>
</div>

---

## What is the AST?

The Abstract Syntax Tree is the structured representation of Python source code after parsing but before compilation to bytecode.

```python
import ast

source = '''
def greet(name):
    return f"Hello, {name}!"
'''

tree = ast.parse(source)
print(ast.dump(tree, indent=2))
```

Output:
```
Module(
  body=[
    FunctionDef(
      name='greet',
      args=arguments(
        args=[arg(arg='name')],
        ...
      ),
      body=[
        Return(
          value=JoinedStr(
            values=[
              Constant(value='Hello, '),
              FormattedValue(value=Name(id='name', ctx=Load()), ...),
              Constant(value='!')
            ]
          )
        )
      ],
      ...
    )
  ]
)
```

---

## Node Types — the building blocks

### Expressions

| Node | Python source | Example |
|---|---|---|
| `Constant(value=42)` | `42` | Literals |
| `Name(id='x')` | `x` | Variable reference |
| `BinOp(left, op, right)` | `a + b` | Binary operations |
| `Call(func, args, keywords)` | `f(x, y=1)` | Function calls |
| `Attribute(value, attr)` | `obj.method` | Attribute access |
| `Subscript(value, slice)` | `x[0]` | Indexing |
| `ListComp(...)` | `[x for x in ...]` | Comprehensions |
| `IfExp(test, body, orelse)` | `a if c else b` | Ternary |

### Statements

| Node | Python source |
|---|---|
| `Assign(targets, value)` | `x = 10` |
| `FunctionDef(name, args, body)` | `def f(): ...` |
| `ClassDef(name, bases, body)` | `class C: ...` |
| `Return(value)` | `return x` |
| `If(test, body, orelse)` | `if ...: ... else: ...` |
| `For(target, iter, body)` | `for x in y: ...` |
| `Import(names)` | `import os` |
| `Raise(exc)` | `raise ValueError()` |

---

## Walking the tree with `NodeVisitor`

```python
import ast

class FunctionAnalyzer(ast.NodeVisitor):
    """Collect information about all functions in a module."""

    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        info = {
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "decorators": [ast.dump(d) for d in node.decorator_list],
            "has_return": any(
                isinstance(n, ast.Return) and n.value is not None
                for n in ast.walk(node)
            ),
        }
        self.functions.append(info)
        self.generic_visit(node)   # visit child nodes

    # Also handles async functions
    visit_AsyncFunctionDef = visit_FunctionDef


source = '''
def add(a, b):
    return a + b

def greet(name):
    print(f"Hello, {name}")

@decorator
async def fetch(url):
    return await get(url)
'''

tree = ast.parse(source)
analyzer = FunctionAnalyzer()
analyzer.visit(tree)

for f in analyzer.functions:
    print(f"{f['name']}({', '.join(f['args'])}) "
          f"line={f['line']} returns={f['has_return']}")

# Output:
# add(a, b) line=2 returns=True
# greet(name) line=5 returns=False
# fetch(url) line=9 returns=True
```

---

## Transforming code with `NodeTransformer`

`NodeTransformer` visits each node and replaces it with the returned node:

```python
import ast

class DebugPrintInjector(ast.NodeTransformer):
    """Add a print() before every assignment to show what's being set."""

    def visit_Assign(self, node):
        # Create a print statement: print(f"SET {target} = {value}")
        target_name = ast.dump(node.targets[0])

        debug_print = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print', ctx=ast.Load()),
                args=[ast.Constant(value=f"DEBUG: assignment at line {node.lineno}")],
                keywords=[],
            )
        )
        ast.fix_missing_locations(debug_print)

        return [debug_print, node]   # inject print BEFORE the assignment


source = '''
x = 10
y = x + 5
z = x * y
'''

tree = ast.parse(source)
tree = DebugPrintInjector().visit(tree)
ast.fix_missing_locations(tree)

code = compile(tree, "<transformed>", "exec")
exec(code)
# Output:
# DEBUG: assignment at line 2
# DEBUG: assignment at line 3
# DEBUG: assignment at line 4
```

---

## Use Case: Automatic Timing of All Functions

```python
import ast, textwrap

class TimerInjector(ast.NodeTransformer):
    """Wrap every function body with timing code."""

    def visit_FunctionDef(self, node):
        self.generic_visit(node)   # recurse into nested functions

        # Create: import time; _start = time.perf_counter()
        setup = ast.parse("import time; _start = time.perf_counter()").body

        # Create: print(f"{name} took {time.perf_counter() - _start:.4f}s")
        teardown = ast.parse(
            f'print(f"{node.name} took {{time.perf_counter() - _start:.4f}}s")'
        ).body

        # Wrap original body in try/finally
        try_node = ast.Try(
            body=node.body,
            handlers=[],
            orelse=[],
            finalbody=teardown,
        )
        ast.fix_missing_locations(try_node)

        node.body = setup + [try_node]
        return node


source = '''
def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

result = slow_function()
print(f"Result: {result}")
'''

tree = ast.parse(source)
tree = TimerInjector().visit(tree)
ast.fix_missing_locations(tree)

exec(compile(tree, "<timed>", "exec"))
# Output:
# slow_function took 0.0412s
# Result: 499999500000
```

---

## Use Case: Security — detecting dangerous calls

```python
import ast

DANGEROUS_CALLS = {'eval', 'exec', 'compile', '__import__', 'open', 'system'}
DANGEROUS_ATTRS = {'__subclasses__', '__globals__', '__code__'}

class SecurityScanner(ast.NodeVisitor):
    def __init__(self):
        self.warnings = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_CALLS:
                self.warnings.append(
                    f"Line {node.lineno}: dangerous call to '{node.func.id}()'"
                )
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in DANGEROUS_ATTRS:
            self.warnings.append(
                f"Line {node.lineno}: access to dangerous attribute '{node.attr}'"
            )
        self.generic_visit(node)


source = '''
import os
user_input = input("Enter expression: ")
result = eval(user_input)
os.system("rm -rf /")
secret = obj.__globals__
'''

tree = ast.parse(source)
scanner = SecurityScanner()
scanner.visit(tree)

for w in scanner.warnings:
    print(f"  ⚠️  {w}")
# Output:
#   ⚠️  Line 4: dangerous call to 'eval()'
#   ⚠️  Line 5: dangerous call to 'system()'
#   ⚠️  Line 6: access to dangerous attribute '__globals__'
```

---

## Use Case: Complexity analysis

```python
import ast

class ComplexityCounter(ast.NodeVisitor):
    """Count cyclomatic complexity of each function."""

    def visit_FunctionDef(self, node):
        complexity = 1   # base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, (ast.For, ast.While)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        print(f"  {node.name}(): complexity = {complexity}")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
```

---

## Compiling and executing transformed ASTs

```python
import ast

source = "x = 1 + 2 * 3"
tree = ast.parse(source)

# Compile AST to code object
code = compile(tree, filename="<ast>", mode="exec")

# Execute
namespace = {}
exec(code, namespace)
print(namespace['x'])   # 7

# Modes:
# "exec"  — module (statements)
# "eval"  — single expression
# "single" — interactive (like REPL)

expr_tree = ast.parse("2 ** 10", mode="eval")
result = eval(compile(expr_tree, "<expr>", "eval"))
print(result)   # 1024
```

---

## `ast.fix_missing_locations`

When you create AST nodes programmatically, they lack line/column info. `fix_missing_locations` copies from parent nodes:

```python
# Always call this after transforming!
tree = MyTransformer().visit(tree)
ast.fix_missing_locations(tree)
code = compile(tree, "<source>", "exec")
```

---

## `ast.unparse` — convert AST back to source (Python 3.9+)

```python
import ast

source = "result = (x + y) * z if flag else default"
tree = ast.parse(source)

# Modify: change variable name
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and node.id == "default":
        node.id = "fallback"

print(ast.unparse(tree))
# Output: result = (x + y) * z if flag else fallback
```

---

## Building AST nodes from scratch

```python
import ast

# Build: def hello(name): return f"Hi, {name}!"
func = ast.FunctionDef(
    name="hello",
    args=ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="name")],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    ),
    body=[
        ast.Return(
            value=ast.JoinedStr(
                values=[
                    ast.Constant(value="Hi, "),
                    ast.FormattedValue(
                        value=ast.Name(id="name", ctx=ast.Load()),
                        conversion=-1,
                        format_spec=None,
                    ),
                    ast.Constant(value="!"),
                ]
            )
        )
    ],
    decorator_list=[],
    returns=None,
)

module = ast.Module(body=[func], type_ignores=[])
ast.fix_missing_locations(module)

code = compile(module, "<generated>", "exec")
namespace = {}
exec(code, namespace)
print(namespace["hello"]("World"))   # Hi, World!
```

---

## Practice Exercises

1. **Write a `NodeVisitor`** that counts all variables, function calls, and imports in a Python file.
2. **Write a `NodeTransformer`** that replaces all `print()` calls with `logging.info()`.
3. **Build a dead code detector** that finds functions defined but never called within a module.
4. **Write an auto-documenter** that generates docstrings for functions that lack them (based on argument names and return type).
5. **Implement a Python → Python minifier** using AST: remove docstrings, comments, shorten variable names.
6. **Build a contract system** that injects precondition/postcondition checks from decorator arguments using AST transformation.
