---
id: kruskal-overview
title: "Kruskal's Algorithm: Minimum Spanning Tree"
subtitle: Sort edges and union-find
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 16
status: published
learning_objectives:
  - Construct an MST using a greedy edge selection
  - Apply union-find for cycle detection
  - Compare with Prim's algorithm
tags: [graphs, mst]
keywords: [kruskal, union find]
concept_ids: [mst, kruskal]
competency_ids: [algorithms]
prerequisite_materials: [graphs-intro, union-find-disjoint-sets, sorting-guide]
follow_up_materials: []
summary: "Step-by-step MST construction with correctness intuition."
last_reviewed: 2025-08-15
---

# Kruskal's Algorithm

Sort edges by weight and add if they don't create a cycle.

## Tools

- Sorting
- Disjoint Set Union (DSU)

## Complexity

O(E log E) dominated by sorting.
