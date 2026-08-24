---
title: Sandboxing
description: RestrictedPython, seccomp, containers, resource limits and safe code execution
---

# Sandboxing <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Why sandbox?

When executing **untrusted code** (user submissions, plugins, REPL), you need to prevent:

- File system access (read/write/delete)
- Network access (data exfiltration)
- System calls (exec, fork, kill)
- Resource exhaustion (CPU, memory, disk)
- Import of dangerous modules (os, subprocess, ctypes)

---

## RestrictedPython — AST-level restriction

```python
from RestrictedPython import compile_restricted, safe_globals

# User-submitted code
user_code = '''
result = sum([x**2 for x in range(10)])
'''

# Compile with restrictions
byte_code = compile_restricted(user_code, '<user_input>', 'exec')

# Safe globals — no access to builtins that could be dangerous
restricted_globals = safe_globals.copy()
restricted_globals['_getiter_'] = iter   # allow iteration
restricted_globals['sum'] = sum          # whitelist specific builtins

# Execute
namespace = {}
exec(byte_code, restricted_globals, namespace)
print(namespace['result'])   # 285

# Dangerous code is blocked at compile time:
dangerous = "import os; os.system('rm -rf /')"
try:
    compile_restricted(dangerous, '<user>', 'exec')
except SyntaxError as e:
    print(f"Blocked: {e}")   # import not allowed
```

---

## Resource limits with `resource` module (Linux)

```python
import resource
import signal

def set_limits(max_cpu_seconds=5, max_memory_mb=256):
    """Set resource limits for the current process."""
    # CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))

    # Memory limit
    max_bytes = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))

    # No file creation
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))

    # No new processes
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out!")

def run_sandboxed(code: str, timeout_seconds: int = 5) -> dict:
    """Execute code with resource limits."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    set_limits(max_cpu_seconds=timeout_seconds, max_memory_mb=128)

    namespace = {"__builtins__": {}}   # no builtins!
    # Whitelist safe builtins
    safe_builtins = {
        "range": range, "len": len, "sum": sum,
        "min": min, "max": max, "abs": abs,
        "int": int, "float": float, "str": str,
        "list": list, "dict": dict, "tuple": tuple,
        "print": print, "enumerate": enumerate,
        "zip": zip, "map": map, "filter": filter,
        "True": True, "False": False, "None": None,
    }
    namespace["__builtins__"] = safe_builtins

    try:
        exec(compile(code, "<sandbox>", "exec"), namespace)
        return {"success": True, "namespace": namespace}
    except TimeoutError:
        return {"success": False, "error": "Timeout"}
    except MemoryError:
        return {"success": False, "error": "Memory limit exceeded"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        signal.alarm(0)   # cancel alarm
```

---

## Docker-based sandboxing (strongest isolation)

```python
import docker
import tempfile

def run_in_container(code: str, timeout: int = 10) -> dict:
    """Execute Python code in an isolated Docker container."""
    client = docker.from_env()

    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        code_path = f.name

    try:
        result = client.containers.run(
            "python:3.13-slim",
            command=f"python /code/script.py",
            volumes={code_path: {"bind": "/code/script.py", "mode": "ro"}},
            mem_limit="128m",        # memory limit
            cpu_period=100000,
            cpu_quota=50000,         # 50% of one CPU
            network_disabled=True,   # no network!
            read_only=True,          # read-only filesystem
            remove=True,             # auto-cleanup
            timeout=timeout,
        )
        return {"success": True, "output": result.decode()}
    except docker.errors.ContainerError as e:
        return {"success": False, "error": e.stderr.decode()}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        import os
        os.unlink(code_path)

# Usage
result = run_in_container("print(sum(range(100)))")
print(result)   # {'success': True, 'output': '4950\n'}

# Dangerous code is safely contained
result = run_in_container("import os; os.system('rm -rf /')")
# Fails — read-only filesystem, no permissions
```

---

## Practice Exercises

1. **Build a code runner** that executes user Python code safely with resource limits.
2. **Implement a whitelist-based sandbox** that only allows specific imports and builtins.
3. **Use Docker** to create isolated execution environments with network disabled.
4. **Test your sandbox** — try to escape using known Python sandbox escape techniques.
5. **Add timeout handling** that kills runaway processes after N seconds.
6. **Build a competitive programming judge** that runs user code safely and checks output.
