---
id: counting-bucket-radix
title: "Counting, Bucket, and Radix Sort"
subtitle: Linear-time sorting under constraints
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 18
status: published
learning_objectives:
  - Understand non-comparison sorts and their constraints
  - Implement counting sort as a stable building block
  - Apply radix sort to large integer keys
tags: [sorting]
keywords: [counting sort, radix, bucket]
concept_ids: [sorting]
competency_ids: [algorithms]
prerequisite_materials: [sorting-guide]
follow_up_materials: []
summary: "Beyond comparison: linear-time sorting techniques."
last_reviewed: 2025-08-15
---

# Non-Comparison Sorting

These methods exploit structure in keys to achieve O(n) under assumptions.

## Counting Sort

Stable, requires bounded key range.

## Bucket Sort

Assumes uniform distribution; sort buckets individually.

## Radix Sort

Processes digits from LSD or MSD using a stable subroutine (often counting sort).
