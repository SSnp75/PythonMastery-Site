---
title: Sorting & Searching
description: Comparison sorts, binary search, merge sort, quick sort and complexity analysis
---

# Sorting & Searching <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🧮 Algorithms · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Binary search — O(log n)

```python
def binary_search(arr: list[int], target: int) -> int:
    """Find target in sorted array. Returns index or -1."""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

# Usage
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
print(binary_search(arr, 7))    # 3 (index)
print(binary_search(arr, 8))    # -1 (not found)
# Searches 1 million items in ~20 comparisons!
```

---

## Merge sort — O(n log n), stable

```python
def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left: list, right: list) -> list:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
# [3, 9, 10, 27, 38, 43, 82]
```

---

## Quick sort — O(n log n) average, in-place

```python
def quick_sort(arr: list, low: int = 0, high: int = None) -> list:
    if high is None:
        high = len(arr) - 1
    if low < high:
        pivot_idx = partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)
    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

---

## Complexity comparison

| Algorithm | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| TimSort (Python) | O(n) | O(n log n) | O(n log n) | O(n) | Yes |

---

## Practice Exercises

1. **Implement binary search** for finding the leftmost occurrence of a value.
2. **Implement merge sort** and count inversions (pairs where `arr[i] > arr[j]` and `i < j`).
3. **Implement quick sort** with random pivot selection (avoid worst case).
4. **Use `bisect`** module for efficient sorted-list operations.
5. **Benchmark** all sorts on 100K random integers — verify theoretical complexities.
