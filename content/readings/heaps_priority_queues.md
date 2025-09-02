---
id: heaps-priority-queues
title: Heaps and Priority Queues
subtitle: Efficient access to min/max elements
author: DSATrain Team
content_type: tutorial
difficulty_level: medium
estimated_read_time: 16
status: published
learning_objectives:
  - Understand heap property and array representation
  - Implement push/pop operations
  - Apply heaps to scheduling and k-way merges
tags: [heaps, priority-queue]
keywords: [binary heap, heapify]
concept_ids: [heaps]
competency_ids: [data_structures]
prerequisite_materials: [trees-intro]
follow_up_materials: [dijkstra-overview]
summary: "Learn heap fundamentals and how priority queues power many algorithms."
last_reviewed: 2025-08-15
---

# Heaps Overview

Heaps maintain a partial order for fast extreme retrieval.

## Binary Heap Representation

Use an array where children of i are 2i+1 and 2i+2.

## Operations

- push: insert and bubble up
- pop: remove top and bubble down

## Applications

- Dijkstra's algorithm
- Top-k problems
- Merging sorted lists
