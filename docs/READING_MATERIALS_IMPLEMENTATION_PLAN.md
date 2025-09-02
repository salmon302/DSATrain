# Reading Materials Feature: Complete Implementation Plan

## Executive Summary

Goal: Ship an end-to-end "Readings" experience tightly integrated with DSATrain’s practice flow, guided by the strategy and research docs. Scope includes DB, API, services, content pipeline, recommendations, analytics, frontend UI, and launch/ops.

Current state (as of repo):
- Backend
  - Models exist: `ReadingMaterial`, `UserReadingProgress`, `MaterialRecommendation`, `MaterialAnalytics`, `ContentCollection` in `src/models/reading_materials.py`.
  - Alembic migration exists: `alembic/versions/006_reading_materials_system.py`.
  - API exists: `src/api/reading_materials_api.py` with search, material detail, progress, rating, collections, analytics, dismiss recommendation.
  - Router not yet wired into main FastAPI app.
  - Recommendation engine(s) exist for problems, not yet wired to readings.
- Frontend
  - No dedicated Readings UI yet.
  - Skill tree and settings pages exist; good patterns to reuse.
- Content
  - Sample materials in `sample_reading_materials/` as Markdown.

Impact: Implement a production-ready readings system with personalization and analytics, and integrate into practice workflows (pre-problem, post-problem, milestones).

---

## Architecture Overview

- Persistence: SQLAlchemy models already defined. Migrations present.
- API layer: New `reading_materials` router to be included in main API. Request/response via Pydantic.
- Services:
  - Content ingestion: parse Markdown, frontmatter metadata, section anchors, TOC.
  - Recommendation: blend rules + lightweight similarity (concept tags) now; extend to embeddings later.
  - Analytics: daily rollups into `MaterialAnalytics` with simple cron/job.
- Frontend:
  - Pages: Readings Home, Material Detail, Collections; inline reading prompts in practice flows.
  - Components: Reader (Markdown + ToC + progress), Recommendation widgets, Ratings/Feedback, Collection Card/Grid.
- Telemetry: Event schema for reads, progress, rating, completion, engagement.

---

## Gaps and Decisions

1) API router wiring
- Wire `src/api/reading_materials_api.py` into `src/api/main.py` via `app.include_router`.

2) Content pipeline (MVP)
- Source: folder `content/readings/**/*.md` (create). Each file with YAML frontmatter for required fields.
- Script to ingest/update DB. Idempotent upsert by `id`.
- Validate required metadata aligns with models: content_type, difficulty_level, estimated_read_time, concept_ids, target_personas, learning_objectives, tags, summary.

3) Recommendations (Phase 1 rules; Phase 2 embeddings)
- Phase 1: Rules based on concept overlap, user gaps (if available), difficulty, and recent activity. Populate `MaterialRecommendation` for `default_user` on demand.
- Phase 2: Add embedding store (pgvector or Chroma/Qdrant). Optional—out of MVP if infra not present.

4) Analytics generation
- Nightly job to roll up `UserReadingProgress` → `MaterialAnalytics` (daily/weekly/monthly). Simple Python job callable via endpoint `/reading-materials/analytics/run-rollup` (admin) and/or a background task.

5) Frontend UX
- Readings Directory (search/filter), Material View (reader with ToC, progress, rating), Collections, and Contextual prompts in practice page.
- Progress: autosave progress % and reading time; basic scroll-depth capture.

6) Testing
- API tests for search, detail, progress, rating, collections, analytics fetch.
- E2E smoke for ingestion.

---

## Data Contracts (Core)

Inputs/Outputs, success/error:
- GET /reading-materials/search
  - in: query, content_type?, difficulty_level?, concept_ids CSV?, user_id?, limit
  - out: list<ReadingMaterialSummary + optional user_progress>
- GET /reading-materials/material/{id}?user_id&include_content=true
  - out: ReadingMaterial full (optionally includes user_progress)
- POST /reading-materials/material/{id}/progress
  - in: user_id, {progress_percentage, reading_time_seconds, sections_read?, notes?, bookmarked_sections?}
  - out: {success, progress}
- POST /reading-materials/material/{id}/rating
  - in: user_id, {user_rating, difficulty_rating?, usefulness_rating?, feedback_text?, would_recommend?}
  - out: {success, material_rating, total_ratings}
- GET /reading-materials/collections
  - out: list<CollectionSummary>
- GET /reading-materials/collection/{id}
  - out: Collection + materials with optional user_progress
- GET /reading-materials/recommendations/{user_id}?context=&problem_id=&limit=
  - out: list<Material with recommendation meta>
- GET /reading-materials/analytics/{material_id}?period=
  - out: analytics payload or message if none

Error modes: 404 for not found, 400 for bad payload, 500 for server.

---

## Services

1) Content Ingest Service (scripts/content_ingest_readings.py)
- Parse markdown with frontmatter (PyYAML + markdown). Required fields validated.
- Build content_sections (headings), estimated_read_time if missing (words / 200 wpm).
- Upsert to DB.

2) Recommendation Service (src/services/reading_recommender.py)
- Rule-based scores:
  - Concept overlap (weight 0.5)
  - Difficulty proximity to user preference/current problem (0.2)
  - Persona match (0.1)
  - Material quality (ratings/effectiveness) (0.2)
- Generate ephemeral list (direct) and/or persist to MaterialRecommendation when contextful.

3) Analytics Rollup (src/services/reading_analytics.py)
- Aggregates daily metrics from `UserReadingProgress` into `MaterialAnalytics`.
- Compute: unique_viewers, total_views, completion_count, average_time, average_rating, distributions.

---

## Frontend Plan (MVP)

- Routes
  - /readings (Directory + search)
  - /readings/collections (Collections grid)
  - /readings/material/:id (Reader)
- Components
  - ReadingCard, CollectionCard, Reader (Markdown render, sticky TOC, progress bar, feedback form), RecommendationRail (pre/post problem)
- Integrations
  - Practice Pages: show contextual readings via `GET /reading-materials/recommendations/{user_id}?context=pre_problem&problem_id=...` and `post_problem`.

---

## Phase Plan

Phase 1 (1-2 weeks)
- Wire router into app
- Create content folder and ingest script
- Seed 5-10 materials from docs (Big-O, Two Pointers, etc.)
- Build frontend Directory and Reader (MVP)
- Progress + Rating endpoint wiring
- Basic rule-based recommendations exposed, shown in practice page sidebar
- API tests for core endpoints

Phase 2 (2 weeks)
- Collections UI + API polish
- Analytics rollup job + admin endpoint
- Recommendation improvements (recent behavior, gaps)
- Search relevance tuning, filters in UI
- Authoring docs and content templates; CMS-lite workflow

Phase 3 (2-3 weeks)
- Embedding-based semantic recommendations (optional infra)
- Interactive elements (quizzes, code walkthroughs)
- A/B testing hooks and metrics dashboards
- Mobile layout polish

---

## Detailed Task Breakdown (Epics → Stories)

1) Database & API
- [ ] Include `reading_materials` router in main app
- [ ] Add admin endpoints: rollup analytics, ingest preview (optional)
- [ ] Tighten Pydantic models (response schemas)
- [ ] Rate limits (reuse existing middleware if any)

2) Content Pipeline
- [ ] Create `content/readings/` with 10 seed materials and YAML frontmatter
- [ ] Implement ingest script with dry-run and upsert
- [ ] Validate and log errors; write summary report

3) Recommendation Engine (Rules)
- [ ] Implement service to compute per-context recommendations
- [ ] Surface via existing API endpoint (augment current behavior)
- [ ] Add unit tests for ranking logic

4) Analytics
- [ ] Implement rollup service
- [ ] Add `/reading-materials/analytics/run-rollup` (admin/dev only)
- [ ] Display analytics snippet in material admin panel (wip)

5) Frontend
- [ ] Directory page with search/filters
- [ ] Reader page with markdown render + ToC + progress capture
- [ ] Collections grid + detail
- [ ] Practice integration: reading suggestions rail
- [ ] Rating/feedback form

6) Tests
- [ ] Backend API tests for search/detail/progress/rating/collections/recommendations
- [ ] Ingestion test (load sample md, assert DB rows)
- [ ] Minimal frontend smoke (if applicable)

7) Ops
- [ ] Alembic migration run step in README
- [ ] Cron or Windows Task Scheduler for analytics job (or manual trigger)

---

## Instrumentation & Metrics (KPIs → Events)

KPIs (from strategy/summary):
- Engagement: completion rate, avg time, ratings
- Effectiveness: post-reading problem improvement
- Conversion: reading → practice; practice success after reading

Events (UserReadingProgress + supplementary events):
- reading_view (material_id, user_id, session_id)
- reading_progress (progress%, time_sec, sections)
- reading_complete (completion)
- reading_rate (rating values)

Rollups in `MaterialAnalytics` with period_type daily/weekly/monthly.

---

## Dependencies and Open Questions

- Embeddings/vector DB optional. If adopted, prefer pgvector with Postgres; otherwise defer.
- Auth/users: current single-user mode uses `default_user`—sufficient for MVP, but design endpoints to accept provided `user_id`.
- Content ownership: start with internal materials; later, contributor workflow.

---

## Risks and Mitigations

- Scope creep: lock MVP to rules-based recommendations and static markdown content.
- Data quality: enforce frontmatter schema and CI check for content files.
- Analytics noise: throttle progress updates (e.g., at section boundaries or 10% increments).

---

## Acceptance Criteria (MVP)

- User can browse readings, open a material, see ToC, progress updates, and rate it.
- Pre/post-problem suggestions appear given problem context.
- Collections render with user progress indicators.
- Nightly analytics job can produce rows in `material_analytics`.
- API endpoints covered by tests; ingestion script loads seed content.

---

## How to Run (initial)

- Apply migrations: ensure Alembic upgrade ran for `006_reading_materials_system`.
- Start API server and frontend as usual.
- Ingest content: run scripts/content_ingest_readings.py with path to content folder.

---

## Next Steps

- Wire router now; add plan issues/tickets; scaffold ingest and services; create seed content files; implement Reader UI skeleton.
