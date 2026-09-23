---
title: "Beginner Projects"
description: Small, finishable projects to build Python confidence
---

# Beginner Projects <span class="pm-badge pm-badge-beginner">Level 1</span>

<div class="pm-topic-header">
  <strong>🛠️ Projects</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Hours to a few days each</span>
    <span>📚 Prereqs: <a href="../core/beginner/python-basics.md">Python Basics</a> → <a href="../core/beginner/file-handling.md">File Handling</a></span>
  </div>
</div>

---

These projects use only what you learn in the Beginner Core Python track: variables, control flow, functions, data structures, and file handling. Each is small enough to finish, which is the whole point.

---

## 1. Number guessing game

**Goal:** the computer picks a random number; the player guesses with "higher/lower" hints.

- **Skills:** loops, conditionals, `random`, `input`, comparison.
- **Minimal version:** guess a number 1-100, print "higher" or "lower", count guesses.
- **Stretch:** difficulty levels, limited guesses, play-again loop, track best score in a file.

```python
import random
secret = random.randint(1, 100)
# loop: read a guess, compare, give a hint, count attempts...
```

## 2. To-do list (CLI)

**Goal:** add, list, complete, and delete tasks from the command line, saved to a file.

- **Skills:** lists/dicts, functions, file read/write (JSON), a menu loop.
- **Minimal version:** add tasks and list them, held in memory.
- **Stretch:** persist to a JSON file (survives restarts), mark done, due dates, priorities. Turn it into a real CLI with `argparse` (see [Automation & Scripting](../automation/scripting.md)).

## 3. Unit / temperature converter

**Goal:** convert between units (C↔F, km↔miles, kg↔lb).

- **Skills:** functions, arithmetic, user input, a menu.
- **Minimal version:** Celsius → Fahrenheit.
- **Stretch:** many unit categories, a reusable conversion table (dict), input validation.

## 4. Word / character counter

**Goal:** read a text file and report word count, line count, and most common words.

- **Skills:** file reading, string methods, `collections.Counter`.
- **Minimal version:** count lines and words in a file.
- **Stretch:** top-N words, ignore common stop-words, handle multiple files. (Uses ideas from [Code Snippets](../reference/code-snippets.md).)

## 5. Simple password generator

**Goal:** generate a random password of a chosen length and character set.

- **Skills:** `random`/`secrets`, strings, functions.
- **Minimal version:** random 12-character password.
- **Stretch:** options for symbols/digits/case, generate several, estimate strength. Use the `secrets` module (not `random`) for anything real — it's cryptographically secure.

## 6. Basic file organizer

**Goal:** sort files in a folder into subfolders by extension.

- **Skills:** `pathlib`, loops, conditionals.
- **Minimal version:** move `.txt` files into a `text/` folder.
- **Stretch:** organize by many types, dry-run mode, a summary report. This is literally the tested example in [Automation & Scripting](../automation/scripting.md) — build it, then compare.

---

## Where to go next

Once a couple of these feel easy, you're ready for [Intermediate Projects](intermediate.md) — real web apps and APIs. First, though: **put one of these on GitHub** with a README. Shipping and sharing is part of the skill.

!!! tip "Add one test"
    Even a beginner project benefits from a single test (e.g. "the converter turns 100°C into 212°F"). It's how you start the testing habit — see the Testing section.
