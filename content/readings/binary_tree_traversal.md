---
id: binary-tree-traversal
title: Binary Tree Traversal Patterns
subtitle: Preorder, Inorder, Postorder, and Level-order
author: DSATrain Team
content_type: tutorial
difficulty_level: easy
estimated_read_time: 18
status: published
learning_objectives:
  - Implement DFS traversals recursively and iteratively
  - Understand when to use each traversal
  - Use BFS for level-order processing
tags: [trees, traversal, bfs, dfs]
keywords: [preorder, inorder, postorder, level-order]
concept_ids: [binary_trees, traversal]
competency_ids: [data_structures]
prerequisite_materials: [trees-intro]
follow_up_materials: [bst-intro]
summary: "Master the fundamental traversal techniques for binary trees."
last_reviewed: 2025-08-15
---

# Traversal Strategies

Traversal means visiting all nodes in a specific order.

## Preorder

Visit root, then left subtree, then right subtree.

```python
def preorder_iter(root):
    if not root:
        return []
    stack, out = [root], []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return out
```

## Inorder

For BSTs, inorder yields sorted order.

## Postorder

Useful for computing dependent results (e.g., subtree sizes).

## Level-order (BFS)

Use a queue to process nodes by depth.
