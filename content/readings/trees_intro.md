---
id: trees-intro
title: "Trees: A Gentle Introduction"
subtitle: Understanding hierarchical data with rooted trees
author: DSATrain Team
content_type: tutorial
difficulty_level: easy
estimated_read_time: 15
status: published
learning_objectives:
  - Recognize tree terminology (root, leaf, parent, child, height, depth)
  - Differentiate between binary trees and general trees
  - Understand basic traversal strategies
tags: [trees, graph-theory, basics]
keywords: [tree, binary tree, traversal, hierarchy]
concept_ids: [trees, binary_trees]
competency_ids: [data_structures]
follow_up_materials: [binary-tree-traversal, bst-intro]
summary: "Learn what trees are, why they're useful, and how to traverse them."
thumbnail_url: null
last_reviewed: 2025-08-15
---

# What is a Tree?

A tree is an acyclic, connected structure that models hierarchical relationships. It consists of nodes and edges, with one designated root node.

## Terminology

- Root: The top-most node of the tree.
- Parent/Child: A directed relationship between two nodes.
- Leaf: A node with no children.
- Depth: Distance from the root to a node.
- Height: Maximum depth of any node.

## Why Trees?

Trees efficiently model hierarchies (file systems, DOM, org charts) and enable logarithmic time operations in balanced variants.

## Binary Trees vs General Trees

- General tree: Any number of children per node.
- Binary tree: Each node has at most two children (left/right).

## Traversals (Overview)

Common traversals:

- Preorder (root, left, right)
- Inorder (left, root, right)
- Postorder (left, right, root)
- Level-order (BFS by levels)

```python
# Example: Preorder traversal (recursive)
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)
```

## Practice Ideas

- Draw a small tree and list preorder/inorder/postorder.
- Explain the difference between depth and height.
