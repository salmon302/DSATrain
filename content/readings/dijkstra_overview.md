---
id: dijkstra-overview
title: "Dijkstra's Algorithm: Shortest Paths"
subtitle: Non-negative weighted graphs
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 18
status: published
learning_objectives:
  - Understand the greedy frontier expansion
  - Use priority queue optimizations
  - Recognize constraints (no negative edges)
tags: [graphs, shortest-path]
keywords: [dijkstra, priority queue]
concept_ids: [dijkstra]
competency_ids: [algorithms]
prerequisite_materials: [graphs-intro, bfs-dfs-graphs, heaps-priority-queues]
follow_up_materials: [shortest-paths-overview]
summary: "A practical walkthrough of Dijkstra's algorithm."
last_reviewed: 2025-08-15
---

# Dijkstra's Algorithm

Maintains a set of nodes with known shortest distances.

## Data Structures

- Priority queue (min-heap)
- Adjacency list

## Complexity

O((V + E) log V) with a binary heap.
