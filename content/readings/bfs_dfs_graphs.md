---
id: bfs-dfs-graphs
title: BFS and DFS on Graphs
subtitle: Traversal templates and use-cases
author: DSATrain Team
content_type: tutorial
difficulty_level: easy
estimated_read_time: 17
status: published
learning_objectives:
  - Implement BFS and DFS on adjacency lists
  - Handle visited sets and cycles
  - Identify when BFS vs DFS is appropriate
tags: [graphs, traversal]
keywords: [bfs, dfs]
concept_ids: [graphs, traversal]
competency_ids: [algorithms]
prerequisite_materials: [graphs-intro]
follow_up_materials: [topological-sort, shortest-paths-overview]
summary: "Learn to traverse graphs safely and efficiently."
last_reviewed: 2025-08-15
---

# BFS

Use a queue; great for shortest path in unweighted graphs.

## DFS

Use recursion or a stack; good for exploring components and detecting cycles.

## Handling Cycles

Maintain a visited set to avoid infinite loops.
