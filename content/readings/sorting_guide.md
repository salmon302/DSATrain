---
id: sorting-guide
title: "Sorting Algorithms: A Practical Guide"
subtitle: When to use which sorting algorithm
author: DSATrain Team
content_type: tutorial
difficulty_level: easy
estimated_read_time: 20
status: published
learning_objectives:
  - Compare time/space complexity of common sorts
  - Understand stability and in-place criteria
  - Choose appropriate sort for problem constraints
tags: [sorting]
keywords: [quick sort, merge sort, heap sort, stability]
concept_ids: [sorting]
competency_ids: [algorithms]
prerequisite_materials: []
follow_up_materials: [counting-bucket-radix]
summary: "A side-by-side comparison of sorting methods."
last_reviewed: 2025-08-15
---

# Overview of Sorting

Different sorts suit different constraints.

## Quicksort

Average O(n log n), worst O(n^2) without careful pivots; in-place.

## Mergesort

O(n log n) stable; needs extra memory.

## Heapsort

O(n log n) in-place; not stable.
