---
title: Graph Algorithms
description: BFS, DFS, Dijkstra, topological sort and shortest path algorithms
---

# Graph Algorithms <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🧮 Algorithms · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## Graph representation

```python
from collections import defaultdict, deque

# Adjacency list (most common)
graph = defaultdict(list)
graph["A"].extend(["B", "C"])
graph["B"].extend(["D", "E"])
graph["C"].extend(["F"])
# A → B, C
# B → D, E
# C → F

# Weighted graph
weighted = defaultdict(list)
weighted["A"].append(("B", 4))
weighted["A"].append(("C", 2))
weighted["B"].append(("D", 3))
```

---

## BFS (Breadth-First Search) — shortest path in unweighted graphs

```python
def bfs(graph, start, target):
    """Find shortest path from start to target."""
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()
        if node == target:
            return path

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None   # no path found

path = bfs(graph, "A", "F")
print(path)   # ['A', 'C', 'F']
```

---

## DFS (Depth-First Search) — explore all paths

```python
def dfs(graph, start, target, visited=None):
    """Find if path exists (recursive)."""
    if visited is None:
        visited = set()
    if start == target:
        return True
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            if dfs(graph, neighbor, target, visited):
                return True
    return False

# Iterative DFS
def dfs_iterative(graph, start):
    """Visit all nodes reachable from start."""
    stack = [start]
    visited = set()
    order = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)

    return order
```

---

## Dijkstra — shortest path in weighted graphs

```python
import heapq

def dijkstra(graph, start):
    """Find shortest distance from start to all nodes."""
    distances = {start: 0}
    priority_queue = [(0, start)]

    while priority_queue:
        dist, node = heapq.heappop(priority_queue)
        if dist > distances.get(node, float('inf')):
            continue

        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                heapq.heappush(priority_queue, (new_dist, neighbor))

    return distances

distances = dijkstra(weighted, "A")
print(distances)   # {'A': 0, 'C': 2, 'B': 4, 'D': 7}
```

---

## Topological sort (DAG ordering)

```python
def topological_sort(graph):
    """Kahn's algorithm — BFS-based topological sort."""
    in_degree = defaultdict(int)
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue = deque([n for n in graph if in_degree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(graph):
        raise ValueError("Graph has a cycle!")
    return order

# Task dependencies
tasks = defaultdict(list)
tasks["build"].append("test")
tasks["test"].append("deploy")
tasks["lint"].append("build")
print(topological_sort(tasks))   # ['lint', 'build', 'test', 'deploy']
```

---

## Cycle detection

```python
def has_cycle(graph):
    """Detect cycle using DFS coloring."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:   # back edge = cycle!
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    return any(dfs(node) for node in graph if color[node] == WHITE)
```

---

## Practice Exercises

1. **Implement BFS** to find the shortest path in a maze (2D grid).
2. **Implement Dijkstra** and find the shortest path between two cities.
3. **Detect a cycle** in a directed graph representing task dependencies.
4. **Topological sort** — determine build order for a project with dependencies.
5. **Find connected components** in an undirected graph using DFS.
6. **Implement A\*** search for pathfinding with heuristics.
