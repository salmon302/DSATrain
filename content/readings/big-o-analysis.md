---
id: big-o-analysis
title: Big-O Analysis Guide
subtitle: Estimating time and space complexity
author: DSATrain Team
content_type: guide
difficulty_level: beginner
estimated_read_time: 10
concept_ids: ["time_complexity", "space_complexity", "asymptotics"]
competency_ids: ["analysis", "estimation"]
prerequisite_materials: []
follow_up_materials: ["two-pointers", "binary-search"]
target_personas: ["foundation_builder"]
learning_objectives:
  - Understand Big-O notation basics
  - Compare common complexities
  - Estimate complexity from code
skill_level_requirements: {}
tags: ["big-o", "complexity", "analysis"]
keywords: ["big o", "time complexity", "space complexity"]
summary: A practical introduction to Big-O notation and how to estimate complexities.
thumbnail_url: ""
status: published
version: "1.0"
last_reviewed: 2025-08-01
published_at: 2025-08-10
---

# Big-O Analysis Guide

Big-O notation describes how the runtime or memory grows with input size n. Focus on dominant terms and drop constants.

## Common Classes

- O(1): constant
- O(log n): logarithmic
- O(n): linear
- O(n log n): n log n
- O(n^2): quadratic
- O(2^n), O(n!): exponential/factorial

## Estimation Patterns

- Nested loops → multiply
- Sequential loops → add (dominant term wins)
- Divide-and-conquer → often O(n log n)

## Practice

Estimate complexities of sample snippets and justify tradeoffs.
