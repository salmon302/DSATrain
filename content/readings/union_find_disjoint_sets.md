---
id: union-find-disjoint-sets
title: Union-Find (Disjoint Sets)
subtitle: Fast connectivity queries with path compression
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 18
status: published
learning_objectives:
  - Implement union by rank and path compression
  - Model connectivity and components
  - Apply to cycle detection and Kruskal's MST
tags: [graphs, union-find]
keywords: [disjoint set, DSU]
concept_ids: [union_find]
competency_ids: [data_structures]
prerequisite_materials: [graphs-intro]
follow_up_materials: [kruskal-overview]
summary: "A practical guide to DSU for dynamic connectivity problems."
last_reviewed: 2025-08-15
---

# The Union-Find Structure

Maintain parent pointers and ranks to track disjoint sets.

## Operations

- find(x): returns representative of x's set
- union(x, y): merges sets

## Optimizations

Path compression and union by rank/size make operations nearly O(1) amortized.
