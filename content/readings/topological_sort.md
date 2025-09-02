---
id: topological-sort
title: "Topological Sort"
subtitle: Ordering DAGs linearly
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 16
status: published
learning_objectives:
  - Identify DAGs and necessary conditions
  - Implement Kahn's algorithm and DFS-based ordering
  - Apply to dependency resolution
tags: [graphs]
keywords: [topological sort, DAG]
concept_ids: [graphs, topo]
competency_ids: [algorithms]
prerequisite_materials: [graphs-intro]
follow_up_materials: []
summary: "Linear ordering of DAG nodes respecting edge directions."
last_reviewed: 2025-08-15
---

# Topological Sort

Only defined for DAGs.

## Kahn's Algorithm

Repeatedly remove nodes with in-degree 0.

## DFS Method

Postorder reverse of DFS finishing times.
