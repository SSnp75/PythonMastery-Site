---
title: Recursion & Backtracking
description: Recursive thinking, backtracking patterns, memoization and tree recursion
---

# Recursion & Backtracking <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🧮 Algorithms · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Recursion fundamentals

```python
# Every recursive function needs:
# 1. Base case (when to stop)
# 2. Recursive case (smaller subproblem)

def factorial(n: int) -> int:
    if n <= 1:          # base case
        return 1
    return n * factorial(n - 1)   # recursive case

def power(base, exp):
    if exp == 0: return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half          # O(log n) — efficient!
    return base * power(base, exp - 1)
```

---

## Backtracking — explore and undo

```python
def permutations(nums: list) -> list[list]:
    """Generate all permutations using backtracking."""
    result = []

    def backtrack(path, remaining):
        if not remaining:
            result.append(path[:])
            return
        for i in range(len(remaining)):
            path.append(remaining[i])
            backtrack(path, remaining[:i] + remaining[i+1:])
            path.pop()   # UNDO — backtrack

    backtrack([], nums)
    return result

print(permutations([1, 2, 3]))
# [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]

def solve_n_queens(n: int) -> list[list[str]]:
    """Place n queens on n×n board so no two attack each other."""
    solutions = []
    board = [["." for _ in range(n)] for _ in range(n)]

    def is_safe(row, col):
        for i in range(row):
            if board[i][col] == "Q": return False
            if col-(row-i) >= 0 and board[i][col-(row-i)] == "Q": return False
            if col+(row-i) < n and board[i][col+(row-i)] == "Q": return False
        return True

    def backtrack(row):
        if row == n:
            solutions.append(["".join(r) for r in board])
            return
        for col in range(n):
            if is_safe(row, col):
                board[row][col] = "Q"
                backtrack(row + 1)
                board[row][col] = "."   # undo

    backtrack(0)
    return solutions

solutions = solve_n_queens(4)
for s in solutions:
    for row in s: print(row)
    print()
```

---

## Practice Exercises

1. **Generate all subsets** of a set using backtracking.
2. **Solve Sudoku** using backtracking with constraint propagation.
3. **Find all paths** in a maze from start to end.
4. **Generate valid parentheses** — all combinations of n pairs.
5. **Word search** — find if a word exists in a 2D character grid.
