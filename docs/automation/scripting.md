---
title: "Automation & Scripting"
description: File system automation, task scheduling, batch processing and OS interaction with Python
---

# Automation & Scripting <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🤖 Automation Track</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prereqs: File Handling, Functions</span>
  </div>
</div>

---

## What you'll learn

- [x] Manipulate files and folders with `pathlib`
- [x] Copy, move, archive and clean up with `shutil`
- [x] Batch-process CSV and JSON data
- [x] Run external programs with `subprocess`
- [x] Read configuration from environment variables
- [x] Schedule scripts to run automatically
- [x] Turn a script into a reusable CLI tool
- [x] Log what your automation does

Automation is where Python earns its "batteries included" reputation. Most of what follows uses only the standard library — no installs required.

---

## 1. File System Automation

### Paths with `pathlib`

`pathlib` is the modern, object-oriented way to work with paths. Prefer it over the older string-based `os.path`.

```python
from pathlib import Path

p = Path("reports") / "2026" / "summary.txt"   # join with /

print(p.name)      # 'summary.txt'  — file name
print(p.stem)      # 'summary'      — name without suffix
print(p.suffix)    # '.txt'         — extension
print(p.parent)    # 'reports/2026' — containing folder
print(p.parts)     # ('reports', '2026', 'summary.txt')
```

**Why `pathlib` over `os.path`:** paths become real objects with methods, the `/` operator reads naturally, and the same code works on Windows and Linux without worrying about `\` vs `/`.

### Reading & writing

```python
from pathlib import Path

f = Path("note.txt")

f.write_text("hello", encoding="utf-8")   # write (creates/overwrites)
content = f.read_text(encoding="utf-8")   # read whole file
# content -> 'hello'

print(f.exists())   # True
print(f.is_file())  # True
print(f.stat().st_size)  # size in bytes
```

!!! tip "Always pass `encoding='utf-8'`"
    Without it, Python uses the platform default, which differs between Windows and Linux and is a common source of "works on my machine" bugs.

### Finding files with `glob`

```python
from pathlib import Path

base = Path(".")

# All .txt files in this folder
for f in base.glob("*.txt"):
    print(f)

# All .py files anywhere below this folder (recursive)
for f in base.rglob("*.py"):
    print(f)
```

`glob` matches one level; `rglob` recurses into subfolders. Both return a generator of `Path` objects.

### Real example: organize files by extension

A classic automation task — sort a messy download folder into subfolders by file type.

```python
from pathlib import Path

def organize(folder: str) -> dict[str, int]:
    """Move each file into a subfolder named after its extension.

    Returns a count of files moved per extension.
    """
    base = Path(folder)
    moved: dict[str, int] = {}

    for item in base.iterdir():
        if item.is_file():
            ext = item.suffix.lstrip(".") or "no_extension"
            target_dir = base / ext
            target_dir.mkdir(exist_ok=True)   # no error if it exists
            item.rename(target_dir / item.name)
            moved[ext] = moved.get(ext, 0) + 1

    return moved

# result = organize("Downloads")
# -> {'txt': 5, 'pdf': 2, 'jpg': 8}
```

**What's happening:** `iterdir()` lists the folder, `suffix.lstrip(".")` turns `.txt` into `txt`, `mkdir(exist_ok=True)` creates the target folder safely, and `rename()` moves the file. The function returns a summary dict so the caller knows what it did.

---

## 2. Copy, Move, Archive with `shutil`

`pathlib` handles single files well; `shutil` handles whole trees and archives.

```python
import shutil

# Copy a single file (preserves metadata)
shutil.copy2("report.txt", "backup/report.txt")

# Copy an entire directory tree
shutil.copytree("src", "backup/src")

# Move a file or folder
shutil.move("old/data.csv", "archive/data.csv")

# Delete a whole tree (careful — no undo)
shutil.rmtree("temp_folder")

# Create a .zip archive of a folder → returns the archive path
archive_path = shutil.make_archive("backup-2026", "zip", "src")
# archive_path -> 'backup-2026.zip'
```

!!! warning "`shutil.rmtree` is irreversible"
    It permanently deletes the folder and everything in it — there's no recycle bin. Double-check the path, and consider printing what will be deleted before doing it.

### Real example: rotating backups

```python
import shutil
from datetime import datetime
from pathlib import Path

def backup(source: str, backup_root: str) -> str:
    """Create a timestamped zip backup of `source`. Returns the archive path."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = Path(backup_root) / f"backup-{stamp}"
    archive = shutil.make_archive(str(dest), "zip", source)
    return archive

# backup("project", "backups")
# -> 'backups/backup-20260830-154210.zip'
```

---

## 3. Batch Processing Data

### CSV files

`csv.DictReader` treats each row as a dict keyed by the header — much easier than counting columns.

```python
import csv
from pathlib import Path

def total_scores(path: str) -> int:
    """Sum the 'score' column across every row."""
    with Path(path).open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return sum(int(row["score"]) for row in reader)

# For a file with rows Alice,90 and Bob,75:
# total_scores("data.csv") -> 165
```

Writing CSV:

```python
import csv

rows = [
    {"name": "Alice", "score": 90},
    {"name": "Bob",   "score": 75},
]

with open("out.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows(rows)
```

!!! tip "`newline=''` on Windows"
    Always open CSV files with `newline=""`. Without it, Windows inserts an extra blank line between every row.

### JSON files

```python
import json
from pathlib import Path

# Read
data = json.loads(Path("config.json").read_text(encoding="utf-8"))

# Modify
data["version"] = 2

# Write back (indent=2 keeps it human-readable)
Path("config.json").write_text(
    json.dumps(data, indent=2), encoding="utf-8"
)
```

### Real example: batch-rename with a counter

```python
from pathlib import Path

def batch_rename(folder: str, prefix: str) -> list[str]:
    """Rename every file to prefix_001.ext, prefix_002.ext, ...

    Returns the list of new names.
    """
    base = Path(folder)
    files = sorted(f for f in base.iterdir() if f.is_file())
    new_names = []
    for i, f in enumerate(files, start=1):
        new_name = f"{prefix}_{i:03d}{f.suffix}"   # 001, 002, ...
        f.rename(base / new_name)
        new_names.append(new_name)
    return new_names

# batch_rename("photos", "vacation")
# -> ['vacation_001.jpg', 'vacation_002.jpg', ...]
```

The `{i:03d}` format pads the number to 3 digits with leading zeros, so files sort correctly.

---

## 4. Running External Programs with `subprocess`

`subprocess.run` executes another program and waits for it to finish.

```python
import subprocess

# Run a command, capture its output
result = subprocess.run(
    ["git", "status", "--short"],
    capture_output=True,   # capture stdout/stderr
    text=True,             # decode bytes → str
    check=True,            # raise if exit code != 0
)

print(result.stdout)      # the command's output
print(result.returncode)  # 0 on success
```

**Key arguments:**

| Argument | What it does |
|---|---|
| `capture_output=True` | Collect stdout and stderr instead of printing them |
| `text=True` | Return strings instead of raw bytes |
| `check=True` | Raise `CalledProcessError` if the command fails |

!!! danger "Pass a list, not a string — and avoid `shell=True`"
    Always pass the command as a list of arguments (`["ls", "-la"]`). Using `shell=True` with untrusted input opens you to shell-injection attacks. If a value comes from a user, keep it as a separate list item so it's treated as data, never as a command.

### Real example: run a command with a timeout

```python
import subprocess

def run_safely(cmd: list[str], timeout: int = 30) -> str:
    """Run a command, return its stdout, or an error message."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            check=True, timeout=timeout,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"Timed out after {timeout}s"
    except subprocess.CalledProcessError as e:
        return f"Failed (exit {e.returncode}): {e.stderr.strip()}"

# run_safely([sys.executable, "-c", "print('hi')"]) -> 'hi'
```

---

## 5. Environment Variables & Configuration

Never hard-code secrets or environment-specific values. Read them from the environment.

```python
import os

# Read with a fallback default
db_host = os.environ.get("DB_HOST", "localhost")
debug   = os.environ.get("DEBUG", "false").lower() == "true"

# Read a required value (raises KeyError if missing)
api_key = os.environ["API_KEY"]
```

Set them before running (PowerShell):
```powershell
$env:DB_HOST = "prod.example.com"
py myscript.py
```

!!! tip "Keep secrets out of your code"
    API keys and passwords belong in environment variables or a secrets manager — never in the source file, and never committed to git. See the Secrets Management topic for the full picture.

---

## 6. Task Scheduling

Two approaches: schedule from **inside** a long-running Python process, or let the **operating system** run your script on a timer.

### In-process scheduling with `sched`

```python
import sched, time

scheduler = sched.scheduler(time.monotonic, time.sleep)

def job(label: str) -> None:
    print(f"Running {label} at {time.strftime('%H:%M:%S')}")

# Run `job` 2 seconds and 4 seconds from now
scheduler.enter(2, priority=1, action=job, argument=("first",))
scheduler.enter(4, priority=1, action=job, argument=("second",))
scheduler.run()   # blocks until all scheduled jobs are done
```

### OS-level scheduling (recommended for real automation)

For anything that should survive reboots, let the OS run it:

- **Windows** — Task Scheduler, or from PowerShell:
  ```powershell
  schtasks /create /tn "DailyBackup" /tr "py C:\scripts\backup.py" /sc daily /st 02:00
  ```
- **Linux/macOS** — cron. Run `crontab -e` and add:
  ```
  0 2 * * * /usr/bin/python3 /home/user/scripts/backup.py
  ```
  (This runs the script every day at 02:00.)

**Which to choose:** use OS scheduling for periodic maintenance jobs (backups, reports). Use in-process scheduling only when the timing logic is part of a larger running application.

---

## 7. Turn a Script into a CLI Tool

`argparse` (standard library) turns a script into a proper command-line tool with `--flags`, help text, and validation.

```python
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files by extension.")
    parser.add_argument("folder", help="folder to organize")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen without moving files")
    parser.add_argument("--count", type=int, default=1,
                        help="number of times to repeat")

    args = parser.parse_args()

    print(f"folder={args.folder}, dry_run={args.dry_run}, count={args.count}")

if __name__ == "__main__":
    main()
```

Now the script has a real interface:
```bash
python organize.py Downloads --dry-run
python organize.py --help          # auto-generated help
```

**Argument types:**

- **Positional** (`"folder"`) — required, order matters.
- **Optional flag** (`--dry-run` with `action="store_true"`) — `True` if present, `False` otherwise.
- **Typed option** (`--count` with `type=int`) — argparse validates and converts for you.

!!! tip "argparse vs Click vs Typer"
    `argparse` needs no install and covers most needs. For bigger tools with subcommands, look at **Click** or **Typer** (covered in the CLI Tools topic) — they reduce boilerplate and add niceties like colored output.

---

## 8. Logging Your Automation

Unattended scripts (scheduled jobs) need logs — you won't be watching the terminal when they run. Use `logging`, not `print`.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("automation.log", encoding="utf-8"),
        logging.StreamHandler(),   # also print to console
    ],
)

log = logging.getLogger(__name__)

log.info("Backup started")
log.warning("Disk usage above 80%%")
log.error("Failed to connect to server")
```

**Why logging beats `print`:**

- **Levels** — filter noise (`DEBUG`, `INFO`, `WARNING`, `ERROR`) without deleting code.
- **Timestamps** — automatic, so you know *when* something happened.
- **Destinations** — send to a file, the console, or both at once.
- **Always on** — a scheduled job's `print` output usually vanishes; a log file persists.

---

## Putting it together

A realistic maintenance script combining several pieces — clean old files, back up, and log:

```python
import argparse
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

log = logging.getLogger("maintenance")

def clean_old_files(folder: Path, max_age_days: int) -> int:
    """Delete files older than `max_age_days`. Returns count deleted."""
    cutoff = time.time() - max_age_days * 86400
    deleted = 0
    for f in folder.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink()
            deleted += 1
            log.info("Deleted old file: %s", f.name)
    return deleted

def backup(source: Path, dest_root: Path) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = shutil.make_archive(str(dest_root / f"bak-{stamp}"), "zip", source)
    log.info("Created backup: %s", archive)
    return archive

def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Daily maintenance job.")
    parser.add_argument("folder")
    parser.add_argument("--max-age", type=int, default=30)
    args = parser.parse_args()

    folder = Path(args.folder)
    log.info("Maintenance started on %s", folder)
    removed = clean_old_files(folder, args.max_age)
    backup(folder, folder.parent)
    log.info("Done. Removed %d old files.", removed)

if __name__ == "__main__":
    main()
```

---

## Quick reference

| Task | Tool | Example |
|---|---|---|
| Join paths | `pathlib.Path` | `Path("a") / "b"` |
| Read/write text | `Path.read_text` / `.write_text` | `p.write_text("x")` |
| Find files | `Path.glob` / `.rglob` | `base.rglob("*.py")` |
| Copy tree | `shutil.copytree` | `copytree(src, dst)` |
| Zip a folder | `shutil.make_archive` | `make_archive("b", "zip", "src")` |
| Read CSV | `csv.DictReader` | `for row in DictReader(fh)` |
| Read/write JSON | `json.loads` / `.dumps` | `json.dumps(d, indent=2)` |
| Run a program | `subprocess.run` | `run([...], check=True)` |
| Read env var | `os.environ.get` | `os.environ.get("KEY", "default")` |
| CLI arguments | `argparse` | `parser.add_argument(...)` |
| Logging | `logging` | `log.info("...")` |

---

## Practice exercises

1. Write a script that finds every `.log` file under a folder (recursively) and reports the total size in megabytes.
2. Build a CLI tool with `argparse` that takes a folder and an extension, and prints how many matching files exist. Add a `--delete` flag that removes them.
3. Write a backup function that keeps only the 5 most recent zip backups in a folder, deleting older ones.
4. Use `subprocess` to run `python --version` and parse out just the version number.
5. Combine `csv` and `logging`: read a CSV of tasks, process each row, and log a success or failure line per row.
