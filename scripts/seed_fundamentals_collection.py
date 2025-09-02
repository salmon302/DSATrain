"""
Seed a curated ContentCollection named "DS&A Fundamentals" using existing reading materials.

Usage (Windows cmd.exe):
  .\.venv\Scripts\python.exe -m scripts.seed_fundamentals_collection

Respects DSATRAIN_DATABASE_URL. Creates or updates the collection id `fundamentals-collection`.
"""

from typing import List
from datetime import datetime
import os

from src.models.database import DatabaseConfig
from src.models.reading_materials import ContentCollection, ReadingMaterial


FUNDAMENTALS_ID = "fundamentals-collection"

# Ordered material IDs (must match ingested frontmatter ids)
FUNDAMENTALS_SEQUENCE: List[str] = [
    # Sorting & basics
    "sorting-guide",
    "counting-bucket-radix",
    # Trees
    "trees-intro",
    "binary-tree-traversal",
    "bst-intro",
    # Heaps
    "heaps-priority-queues",
    # Graphs core
    "graphs-intro",
    "bfs-dfs-graphs",
    "union-find-disjoint-sets",
    # Graphs advanced
    "topological-sort",
    "dijkstra-overview",
    "shortest-paths-overview",
    # Strategy
    "greedy-algorithms",
    "backtracking-intro",
]


def main() -> None:
    db = DatabaseConfig()
    session = db.get_session()
    try:
        # Filter to only include materials that exist and are published
        existing_ids = {
            r.id for r in session.query(ReadingMaterial)
            .filter(ReadingMaterial.id.in_(FUNDAMENTALS_SEQUENCE))
            .filter(ReadingMaterial.status == "published").all()
        }
        ordered_existing = [rid for rid in FUNDAMENTALS_SEQUENCE if rid in existing_ids]

        if not ordered_existing:
            print("No published reading materials found for Fundamentals collection. Did you run ingestion?")
            return

        collection = session.query(ContentCollection).filter(ContentCollection.id == FUNDAMENTALS_ID).first()
        is_new = collection is None
        if is_new:
            collection = ContentCollection(id=FUNDAMENTALS_ID)
            session.add(collection)

        collection.name = "DS&A Fundamentals"
        collection.description = (
            "A curated sequence of foundational readings covering sorting, trees, heaps, and core graph algorithms."
        )
        collection.collection_type = "learning_path"
        collection.difficulty_level = "mixed"
        collection.estimated_time_hours = int(round(sum(
            (m.estimated_read_time or 10) for m in session.query(ReadingMaterial)
            .filter(ReadingMaterial.id.in_(ordered_existing)).all()
        ) / 3))  # heuristic: 3 min of focused reading ~= 1 hour with exercises

        collection.material_ids = ordered_existing
        collection.material_order = {rid: idx for idx, rid in enumerate(ordered_existing)}
        collection.prerequisites = []
        collection.target_personas = ["foundation_builder", "interview_prep"]
        collection.learning_objectives = [
            "Build a solid foundation in core data structures and graph algorithms",
            "Understand when to use each technique and its complexity trade-offs",
        ]
        collection.skill_outcomes = [
            "Sorting strategies and stability/space trade-offs",
            "Tree traversals and BST fundamentals",
            "Heaps for priority scheduling and shortest paths",
            "Graph traversal, connectivity, topological ordering, and shortest paths",
            "Greedy and backtracking strategy patterns",
        ]
        collection.tags = ["curriculum", "fundamentals", "learning_path"]
        collection.author = "DSATrain Team"
        collection.status = "active"

        session.commit()
        print(("Created" if is_new else "Updated") + f" collection {FUNDAMENTALS_ID} with {len(ordered_existing)} materials")
    finally:
        session.close()


if __name__ == "__main__":
    main()


