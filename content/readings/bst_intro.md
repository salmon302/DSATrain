---
id: bst-intro
title: "Binary Search Trees: Fundamentals"
subtitle: Ordered trees for fast lookup
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 20
status: published
learning_objectives:
  - Understand BST invariant and operations (search/insert/delete)
  - Recognize balanced vs skewed trees
  - Know when to prefer BSTs vs arrays or hash tables
tags: [trees, bst]
keywords: [binary search tree, insert, delete]
concept_ids: [bst]
competency_ids: [data_structures]
prerequisite_materials: [binary-tree-traversal]
follow_up_materials: [balanced-trees-overview]
summary: "A practical guide to BSTs, their invariants, and operations."
last_reviewed: 2025-08-15
---

# What is a BST?

A BST maintains: left subtree < node < right subtree.

## Search

Average O(log n), worst O(n) if skewed.

## Insert/Delete

Rotations are not part of vanilla BST; balancing is provided by variants.

```python
class BST:
    def __init__(self):
        self.root = None
    # ... implementation outline ...
```
