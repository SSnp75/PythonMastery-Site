---
title: CLI Tools
description: Build command-line interfaces with argparse, click and typer
---

# CLI Tools <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="../../core/beginner/functions/">Functions</a></span>
  </div>
</div>

---

## argparse (built-in)

```python
import argparse

parser = argparse.ArgumentParser(description="Greet someone")
parser.add_argument("name", help="Name to greet")
parser.add_argument("-n", "--times", type=int, default=1, help="Times to greet")

args = parser.parse_args()
for _ in range(args.times):
    print(f"Hello, {args.name}!")
```

```bash
python greet.py Alice --times 3
```

---

## click (third-party, declarative)

```python
import click

@click.command()
@click.argument("name")
@click.option("--times", "-n", default=1, help="Times to greet")
def greet(name, times):
    """Greet someone NAME times."""
    for _ in range(times):
        click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

---

## typer (modern, type-hint based)

```python
import typer

app = typer.Typer()

@app.command()
def greet(name: str, times: int = 1):
    """Greet someone."""
    for _ in range(times):
        typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

---

## When to use what

| Tool | Best for |
|---|---|
| `argparse` | Standard library, no deps, simple scripts |
| `click` | Multi-command CLIs, complex options |
| `typer` | Modern apps, type hints, auto-completion |

---

## Practice exercises

1. Build a file search CLI: `finder --ext .py --path ./src`
2. Create a multi-command CLI with `add`, `remove`, `list` subcommands.
3. Add auto-completion and colored output with typer/rich.
