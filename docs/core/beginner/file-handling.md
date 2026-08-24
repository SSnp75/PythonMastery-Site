---
title: File Handling
description: Reading, writing and managing files in Python
---

# File Handling <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="data-structures/">Data Structures</a></span>
  </div>
</div>

---

## Reading files

```python
# Always use 'with' — it closes the file automatically
with open("data.txt", "r") as f:
    content = f.read()          # entire file as string

with open("data.txt", "r") as f:
    lines = f.readlines()       # list of lines (with \n)

# Best: iterate line by line (memory efficient)
with open("data.txt", "r") as f:
    for line in f:
        print(line.strip())
```

---

## Writing files

```python
# Write (overwrites existing)
with open("output.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("Second line\n")

# Append (adds to end)
with open("log.txt", "a") as f:
    f.write("New log entry\n")

# Write multiple lines
lines = ["line 1\n", "line 2\n", "line 3\n"]
with open("output.txt", "w") as f:
    f.writelines(lines)
```

---

## pathlib (modern approach)

```python
from pathlib import Path

# Create path objects
file = Path("data") / "input.txt"

# Read / write
content = file.read_text()
file.write_text("new content")

# Check existence
file.exists()
file.is_file()
file.is_dir()

# List directory
for item in Path(".").iterdir():
    print(item.name)

# Glob patterns
for py_file in Path(".").glob("**/*.py"):
    print(py_file)
```

---

## Working with CSV

```python
import csv

# Read CSV
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["score"])

# Write CSV
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "score": 95})
```

---

## Working with JSON

```python
import json

# Read JSON
with open("config.json", "r") as f:
    data = json.load(f)

# Write JSON
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

# String conversion
json_str = json.dumps({"name": "Alice"})
obj      = json.loads(json_str)
```

---

## Practice exercises

1. Write a program that counts the number of words in a text file.
2. Read a CSV file and print only rows where the score is above 80.
3. Create a simple note-taking app that appends notes to a file.
4. Write a script that finds all `.py` files in a directory tree using `pathlib`.
