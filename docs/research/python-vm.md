---
title: Building a Python VM
description: Implement a bytecode virtual machine from scratch that executes Python .pyc files
---

# Building a Python VM <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: <a href="../core/advanced/bytecode/">Bytecode</a>, <a href="../core/advanced/execution-model/">Execution Model</a></span>
  </div>
</div>

---

## Architecture of a Python VM

```
┌─────────────────────────────────────────┐
│            Python VM                     │
├────────────┬────────────────────────────┤
│  Bytecode  │  Stack Machine             │
│  Loader    │  ├── Operand Stack         │
│            │  ├── Local Variables        │
│            │  ├── Frame Stack            │
│            │  └── Instruction Pointer    │
├────────────┼────────────────────────────┤
│  Object    │  Built-in                  │
│  System    │  Functions                  │
└────────────┴────────────────────────────┘
```

---

## Step 1: The operand stack

```python
class Frame:
    """A single execution frame (one per function call)."""

    def __init__(self, code_obj, global_ns, local_ns):
        self.code = code_obj
        self.stack = []           # operand stack
        self.locals = local_ns    # local variable dict
        self.globals = global_ns  # global variable dict
        self.ip = 0              # instruction pointer (byte offset)

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def next_instruction(self):
        """Read the next opcode and argument."""
        code = self.code.co_code
        op = code[self.ip]
        arg = code[self.ip + 1]   # Python 3.6+: always 2 bytes per instruction
        self.ip += 2
        return op, arg
```

---

## Step 2: The eval loop

```python
import dis
import opcode as op_module

class MiniPythonVM:
    """A minimal Python bytecode interpreter."""

    def __init__(self):
        self.frames = []   # call stack

    def run_code(self, code_obj, global_ns=None):
        global_ns = global_ns or {"__builtins__": __builtins__}
        frame = Frame(code_obj, global_ns, {})
        return self.eval_frame(frame)

    def eval_frame(self, frame):
        self.frames.append(frame)

        while frame.ip < len(frame.code.co_code):
            opcode, arg = frame.next_instruction()
            opname = dis.opname[opcode]

            # Dispatch
            handler = getattr(self, f"op_{opname}", None)
            if handler:
                result = handler(frame, arg)
                if result is not None:   # RETURN_VALUE
                    self.frames.pop()
                    return result
            else:
                raise NotImplementedError(f"Opcode not implemented: {opname} ({opcode})")

        self.frames.pop()

    # ─── Stack operations ─────────────────────────
    def op_LOAD_CONST(self, frame, arg):
        frame.push(frame.code.co_consts[arg])

    def op_POP_TOP(self, frame, arg):
        frame.pop()

    def op_DUP_TOP(self, frame, arg):
        frame.push(frame.peek())

    # ─── Name operations ──────────────────────────
    def op_LOAD_FAST(self, frame, arg):
        name = frame.code.co_varnames[arg]
        frame.push(frame.locals[name])

    def op_STORE_FAST(self, frame, arg):
        name = frame.code.co_varnames[arg]
        frame.locals[name] = frame.pop()

    def op_LOAD_GLOBAL(self, frame, arg):
        name = frame.code.co_names[arg]
        if name in frame.globals:
            frame.push(frame.globals[name])
        elif name in frame.globals.get("__builtins__", {}):
            frame.push(frame.globals["__builtins__"][name])
        else:
            raise NameError(f"name '{name}' is not defined")

    def op_STORE_GLOBAL(self, frame, arg):
        name = frame.code.co_names[arg]
        frame.globals[name] = frame.pop()

    # ─── Arithmetic ───────────────────────────────
    def op_BINARY_ADD(self, frame, arg):
        b = frame.pop()
        a = frame.pop()
        frame.push(a + b)

    def op_BINARY_SUBTRACT(self, frame, arg):
        b = frame.pop()
        a = frame.pop()
        frame.push(a - b)

    def op_BINARY_MULTIPLY(self, frame, arg):
        b = frame.pop()
        a = frame.pop()
        frame.push(a * b)

    def op_BINARY_TRUE_DIVIDE(self, frame, arg):
        b = frame.pop()
        a = frame.pop()
        frame.push(a / b)

    # ─── Comparison ───────────────────────────────
    def op_COMPARE_OP(self, frame, arg):
        CMP_OPS = ['<', '<=', '==', '!=', '>', '>=']
        b = frame.pop()
        a = frame.pop()
        op = CMP_OPS[arg]
        result = eval(f"a {op} b", {"a": a, "b": b})
        frame.push(result)

    # ─── Control flow ─────────────────────────────
    def op_POP_JUMP_IF_FALSE(self, frame, arg):
        value = frame.pop()
        if not value:
            frame.ip = arg

    def op_POP_JUMP_IF_TRUE(self, frame, arg):
        value = frame.pop()
        if value:
            frame.ip = arg

    def op_JUMP_ABSOLUTE(self, frame, arg):
        frame.ip = arg

    def op_JUMP_FORWARD(self, frame, arg):
        frame.ip += arg

    # ─── Function calls ───────────────────────────
    def op_CALL_FUNCTION(self, frame, arg):
        args = [frame.pop() for _ in range(arg)][::-1]
        func = frame.pop()

        if callable(func) and not hasattr(func, '__code__'):
            # Built-in function
            frame.push(func(*args))
        else:
            # User-defined function
            result = self.call_function(func, args)
            frame.push(result)

    def call_function(self, func, args):
        """Call a user-defined function."""
        code = func.__code__
        local_ns = dict(zip(code.co_varnames[:len(args)], args))
        new_frame = Frame(code, func.__globals__, local_ns)
        return self.eval_frame(new_frame)

    # ─── Return ───────────────────────────────────
    def op_RETURN_VALUE(self, frame, arg):
        return frame.pop()

    # ─── Build containers ─────────────────────────
    def op_BUILD_LIST(self, frame, arg):
        items = [frame.pop() for _ in range(arg)][::-1]
        frame.push(items)

    def op_BUILD_TUPLE(self, frame, arg):
        items = tuple(frame.pop() for _ in range(arg))[::-1]
        frame.push(items)
```

---

## Step 3: Running real Python code

```python
# Compile Python source to bytecode, then run in our VM
source = """
x = 10
y = 20
z = x + y
"""

code = compile(source, "<vm-test>", "exec")
vm = MiniPythonVM()
vm.run_code(code)
# z = 30 in the frame's globals

# With a function
source = """
def add(a, b):
    return a + b

result = add(3, 4)
"""

code = compile(source, "<vm-test>", "exec")
vm.run_code(code)
# result = 7
```

---

## What's missing (for a complete VM)

| Feature | Complexity |
|---|---|
| Exception handling (`try/except`) | Medium — needs exception stack |
| Closures (`LOAD_DEREF`) | Medium — cell objects |
| Generators (`yield`) | High — coroutine frames |
| Classes | High — `BUILD_CLASS`, metaclasses |
| Imports | High — module system |
| Attribute access | Medium — `LOAD_ATTR`, `STORE_ATTR` |
| Iteration (`FOR_ITER`) | Medium — iterator protocol |

---

## Practice Exercises

1. **Implement the basic VM** above and run `1 + 2 * 3`.
2. **Add `if/else` support** — implement `POP_JUMP_IF_FALSE` and test conditionals.
3. **Add function calls** — implement `CALL_FUNCTION` and `RETURN_VALUE`.
4. **Add `for` loops** — implement `GET_ITER`, `FOR_ITER`.
5. **Add exception handling** — implement `SETUP_FINALLY`, `POP_EXCEPT`.
6. **Run a real `.pyc` file** — load with `marshal` and execute in your VM.
