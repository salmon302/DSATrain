---
id: backtracking-intro
title: "Backtracking: Systematic Search with Pruning"
subtitle: Explore configuration spaces efficiently
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 20
status: published
learning_objectives:
  - Recognize backtracking patterns for subsets, permutations, and combinations
  - Implement pruning and bounding strategies
  - Use recursion templates safely (state, choices, constraints)
tags: [backtracking]
keywords: [dfs search, pruning]
concept_ids: [backtracking]
competency_ids: [algorithms]
prerequisite_materials: [graphs-intro]
follow_up_materials: []
summary: "Templates and techniques for search problems."
last_reviewed: 2025-08-15
---

# Backtracking

Enumerate solutions by exploring choices and undoing them.

## Template

1. Choose a decision
2. Recurse
3. Undo the choice

## Pruning

Cut branches that cannot lead to a valid or better solution.
