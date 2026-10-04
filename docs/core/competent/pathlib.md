---
title: Pathlib
description: Modern filesystem paths with pathlib.Path — building paths, inspecting, globbing, reading and writing
---

# Pathlib <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="../beginner/file-handling/">File Handling</a></span>
  </div>
</div>

---

`pathlib.Path` is the modern, object-oriented way to work with filesystem paths. It replaces
most of `os.path` with cleaner, cross-platform code.

---

## Building paths

*Building paths in Pathlib — what it is and when to use it.*

The `/` operator joins path segments — no manual separators:

```python
from pathlib import Path

p = Path("project") / "src" / "main.py"
print(p.as_posix())   # project/src/main.py  (forward slashes on any OS)
```

---

## Inspecting a path

*Inspecting a path in Pathlib — what it is and when to use it.*

```python
from pathlib import PurePosixPath

p = PurePosixPath("/home/user/report.final.txt")
print(p.name)      # report.final.txt
print(p.stem)      # report.final
print(p.suffix)    # .txt
print(p.suffixes)  # ['.final', '.txt']
print(p.parent.as_posix())   # /home/user
print(p.parts)     # ('/', 'home', 'user', 'report.final.txt')
```

!!! note "`parts` and the root differ by OS"
    This uses `PurePosixPath` so the output is identical everywhere. A plain `Path` on
    Windows would show a `'\\'` root segment. For OS-agnostic examples, `PurePosixPath` /
    `PureWindowsPath` let you reason about paths without touching the real filesystem.

---

## Changing parts

*Changing parts in Pathlib — what it is and when to use it.*

```python
from pathlib import Path

p = Path("data/input.csv")
print(p.with_suffix(".json").as_posix())   # data/input.json
print(p.with_name("output.csv").as_posix())  # data/output.csv
print(p.with_stem("final").as_posix())       # data/final.csv  (3.9+)
```

---

## Current, home, absolute

*Current, home, absolute in Pathlib — what it is and when to use it.*

```python
from pathlib import Path

print(Path.cwd().is_absolute())    # True
print(Path.home().is_absolute())   # True
print(Path("x").resolve().is_absolute())   # True
```

---

## Existence & type checks

*Existence & type checks in Pathlib — what it is and when to use it.*

```python
from pathlib import Path

p = Path(".")
print(p.exists())    # True
print(p.is_dir())    # True
print(p.is_file())   # False
```

---

## Reading & writing (one-liners)

*Reading & writing (one-liners) in Pathlib — what it is and when to use it.*

```python
from pathlib import Path
import tempfile

d = Path(tempfile.mkdtemp())
f = d / "note.txt"

f.write_text("hello", encoding="utf-8")   # returns chars written
print(f.read_text(encoding="utf-8"))      # hello

f.write_bytes(b"\x00\x01")
print(f.read_bytes())                      # b'\x00\x01'
```

---

## Globbing

*Globbing in Pathlib — what it is and when to use it.*

```python
from pathlib import Path
import tempfile

d = Path(tempfile.mkdtemp())
(d / "a.py").write_text("")
(d / "b.py").write_text("")
(d / "c.txt").write_text("")

py = sorted(p.name for p in d.glob("*.py"))
print(py)   # ['a.py', 'b.py']
```

Use `rglob("*.py")` for a recursive search through all subdirectories.

---

## Creating & removing

*Creating & removing in Pathlib — what it is and when to use it.*

```python
from pathlib import Path
import tempfile

base = Path(tempfile.mkdtemp())
nested = base / "x" / "y"
nested.mkdir(parents=True, exist_ok=True)   # make intermediate dirs
print(nested.exists())   # True

f = nested / "t.txt"
f.write_text("x")
f.unlink()               # delete the file
print(f.exists())        # False
```

!!! tip "Prefer pathlib over os.path"
    `Path("a") / "b"` is clearer and OS-agnostic versus `os.path.join("a", "b")`, and the
    read/write one-liners replace boilerplate `open(...)` blocks for small files.

---

## Practice exercises

1. Given a path, print its extension and the filename without extension.
2. Count all `.md` files under a directory tree using `rglob`.
3. Build a path to `~/.config/app/settings.json` using `Path.home()`.
4. Write and then read back a text file using only `Path` methods.
