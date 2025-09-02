---
id: two-pointers
title: Two Pointers Pattern
subtitle: Efficient scanning over arrays and strings
author: DSATrain Team
content_type: tutorial
difficulty_level: beginner
estimated_read_time: 12
concept_ids: ["two_pointers", "arrays", "strings"]
competency_ids: ["pattern_recognition"]
prerequisite_materials: ["big-o-analysis"]
follow_up_materials: ["sliding-window", "binary-search"]
target_personas: ["pattern_recognizer"]
learning_objectives:
  - Recognize when two pointers applies
  - Implement classic two-pointer solutions
  - Analyze tradeoffs vs. brute force
skill_level_requirements: {}
tags: ["two-pointers", "patterns"]
keywords: ["two pointers", "array techniques"]
summary: Learn the two pointers pattern with examples and pitfalls.
thumbnail_url: ""
status: published
version: "1.0"
last_reviewed: 2025-08-01
published_at: 2025-08-10
---

# Two Pointers Pattern

The two pointers technique uses two indices to traverse a sequence more efficiently than nested loops.

## When to Use

- Finding pairs/triplets under constraints
- Sorting or partitioning in-place
- Comparing sequences from both ends

## Example

Given a sorted array, find if any pair sums to target in O(n).
