---
title: Dynamic Programming
description: Memoization, tabulation, common DP patterns and problem-solving approach
---

# Dynamic Programming <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🧮 Algorithms · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## The DP approach

1. Define the **subproblem** (what are we computing?)
2. Write the **recurrence** (how does current depend on smaller subproblems?)
3. Identify **base cases**
4. Choose **top-down** (memoization) or **bottom-up** (tabulation)

---

## Fibonacci — classic DP example

```python
from functools import lru_cache

# ─── Naive recursion — O(2^n) exponential! ────────
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# ─── Top-down (memoization) — O(n) ───────────────
@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

# ─── Bottom-up (tabulation) — O(n), O(1) space ───
def fib_tab(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

print(fib_tab(50))   # 12586269025 (instant!)
```

---

## Classic DP problems

### 1. Climbing stairs (n ways to climb n steps, 1 or 2 at a time)

```python
def climb_stairs(n: int) -> int:
    if n <= 2: return n
    a, b = 1, 2
    for _ in range(3, n+1):
        a, b = b, a + b
    return b

print(climb_stairs(5))   # 8 ways
```

### 2. Coin change (minimum coins to make amount)

```python
def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1

print(coin_change([1, 5, 10, 25], 30))   # 2 (25 + 5)
print(coin_change([2], 3))                # -1 (impossible)
```

### 3. Longest Common Subsequence

```python
def lcs(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]

print(lcs("abcde", "ace"))      # 3 ("ace")
print(lcs("abc", "abc"))        # 3
print(lcs("abc", "def"))        # 0
```

### 4. 0/1 Knapsack

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]   # don't take item i
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][capacity]

weights = [2, 3, 4, 5]
values  = [3, 4, 5, 6]
print(knapsack(weights, values, 8))   # 10
```

---

## Practice Exercises

1. **Solve coin change** and reconstruct which coins were used.
2. **Longest Increasing Subsequence** — find it in O(n log n).
3. **Edit distance** — minimum insertions/deletions/substitutions to transform one string to another.
4. **Matrix chain multiplication** — optimal parenthesization order.
5. **House robber** — max money robbing non-adjacent houses.
