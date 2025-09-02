# Readings Content and Ingestion

This document explains where reading materials live and how to ingest them into the DSATrain database.

## Where content lives

- Path: `content/readings/`
- Format: Markdown with YAML frontmatter. Required fields in frontmatter:
  - `id` (string, unique)
  - `title` (string)
  - `content_type` (guide|reference|tutorial|case_study|interactive)
  - `difficulty_level` (beginner|intermediate|advanced)
  - `estimated_read_time` (int minutes)
- Recommended optional fields: `subtitle`, `author`, `concept_ids`, `competency_ids`, `prerequisite_materials`, `follow_up_materials`, `target_personas`, `learning_objectives`, `tags`, `keywords`, `summary`, `status` (published|draft), `published_at` (YYYY-MM-DD)

Example file header:

---
id: two-pointers
title: Two Pointers Pattern
content_type: tutorial
difficulty_level: beginner
estimated_read_time: 12
status: published
---

## Ingestion script

Script: `scripts/content_ingest_readings.py`

- Parses YAML frontmatter + Markdown body
- Validates required fields
- Upserts into `reading_materials` table by `id`
- Extracts a basic table of contents from `##` headings into `content_sections`
- Idempotent: re-running updates existing rows without duplicates

### Run on Windows (cmd.exe)

First ensure dependencies are installed (PyYAML is required):

- If using pip: ensure your virtual environment is active
- Run the script:

```
.\.venv\Scripts\python.exe -m scripts.content_ingest_readings --path content\readings
```

Optional flags:

- `--publish-status published|draft` to override frontmatter status
- `--dry-run` to preview without committing

### Expected output

A JSON summary like:

```
{
  "created": 6,
  "updated": 1,
  "errors": []
}
```

## Troubleshooting

- If you see `PyYAML is required`, install with `pip install PyYAML`.
- For SQLite file locking on Windows, close other processes using the DB.
- Ensure `DSATRAIN_DATABASE_URL` is set if you want to target a non-default DB.

## Next steps

- Add more readings under `content/readings/`
- Hook up frontend directory and reader pages to `/reading-materials` endpoints
- Implement analytics rollups for `material_analytics`
