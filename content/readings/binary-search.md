---
id: binary-search
title: Binary Search Variations
subtitle: Lower bounds, upper bounds, and beyond
author: DSATrain Team
content_type: guide
difficulty_level: beginner
estimated_read_time: 15
concept_ids: ["binary_search", "searching", "sorted_structures"]
competency_ids: ["abstraction"]
prerequisite_materials: ["two-pointers"]
follow_up_materials: ["binary-search-on-answer", "search-on-monotonic-functions"]
target_personas: ["foundation_builder", "pattern_recognizer"]
learning_objectives:
  - Implement binary search templates
  - Use lower/upper bound variants
  - Apply search-on-answer on monotonic predicates
skill_level_requirements: {}
tags: ["binary-search", "search"]
keywords: ["lower_bound", "upper_bound", "binary search template"]
summary: A practical guide to robust binary search patterns and pitfalls.
thumbnail_url: ""
status: published
version: "1.0"
last_reviewed: 2025-08-01
published_at: 2025-08-10
---

# Binary Search Variations

Binary search generalizes to any monotonic predicate, not just arrays.

## Templates

- Classic inclusive midpoint
- Lower bound (first true)
- Upper bound (last true)

## Pitfalls

- Infinite loop from mid calc with ints
- Off-by-one on boundaries
