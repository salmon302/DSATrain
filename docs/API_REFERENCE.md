# DSATrain API Reference

This document lists the primary FastAPI endpoints currently exposed by the backend. It focuses on implemented routes validated from the codebase. For OpenAPI docs, run the server and visit http://localhost:8000/docs.

Note: Base path is http://localhost:8000 unless specified. Methods are shown explicitly.

## Health & System
- GET /                           — Service info
- GET /health                     — Health check

## Settings
- GET    /settings                          — Get current settings (optionally include providers/effective flags via query)
- PUT    /settings                          — Update settings (supports api_keys masking)
- GET    /settings/providers                 — Allowed AI providers + UI notes
- GET    /settings/effective                 — Secrets-safe effective settings with api_keys_present flags
- POST   /settings/validate                  — Validate a proposed settings change without saving

## AI
- POST   /ai/hint                            — Return conceptual/structural/concrete hints for a problem
- POST   /ai/review                          — Heuristic code review (local-first, no external calls)
- POST   /ai/elaborate                       — “Why/How” elaboration prompts
- GET    /ai/status                          — AI enablement, provider/model, rate-limit state; optional session_id
- POST   /ai/reset                           — Reset global bucket and/or per-session hint usage

Rate limiting and hint budgets apply. When disabled or provider is "none", AI endpoints return 403. When global rate exceeded, responses return 429 with Retry-After.

## Practice
- POST   /practice/session                    — Generate a practice session (size, difficulty, focus_areas, interleaving)
- POST   /practice/attempt                    — Log a problem attempt (status, time_spent, code, etc.)
- POST   /practice/elaborative                — Create an elaborative interrogation entry
- POST   /practice/working-memory-check       — Submit working memory metrics to adapt UI

### Gated Practice
- POST   /practice/gates/start                — Begin a gated session for a problem (optional session_id)
- POST   /practice/gates/progress             — Update a gate value in a session
- GET    /practice/gates/status               — Get the current status for a session (query: session_id)
- GET    /practice/gates                      — List configured gates (optional query: problem_id)
- GET    /practice/gates/{session_id}         — Fetch a single gated session
- DELETE /practice/gates/{session_id}         — Delete a gated session

## Interview
- POST   /interview/start                     — Start a coding interview session (problem_id, duration, constraints)
- POST   /interview/complete                  — Submit code/metrics to complete an interview session

## Cognitive
- GET    /cognitive/profile                   — Retrieve cognitive profile (query: user_id)
- POST   /cognitive/assess                    — Submit cognitive assessment inputs
- GET    /cognitive/adaptation                — Get adaptation hints (query: user_id)

## Learning Paths
- GET    /learning-paths/templates            — List available learning path templates (filters supported)
- GET    /learning-paths/templates/recommendations
                                              — Get template recommendations (user_goals, available_weeks, current_skill_level)
- POST   /learning-paths/generate             — Generate a personalized learning path from a user profile (optional template_id)
- POST   /learning-paths/quick-start          — Create a beginner-friendly path with minimal input (preset-based)
- GET    /learning-paths/{path_id}            — Retrieve a specific learning path; include milestones by default
- GET    /learning-paths/{path_id}/next-problems — Get next problems with optional context (count)
- POST   /learning-paths/{path_id}/progress   — Update progress after completing a problem
- POST   /learning-paths/{path_id}/adapt      — Adapt path based on performance data
- GET    /learning-paths/user/{user_id}       — List user paths (optional status filter)
- GET    /learning-paths/{path_id}/milestones — List milestones; optionally exclude completed
- POST   /learning-paths/{path_id}/milestones/{milestone_id}/complete
                                              — Mark milestone completed with assessment results
- GET    /learning-paths/analytics/overview   — Analytics overview for learning paths
- POST   /learning-paths/admin/initialize-templates
                                              — Admin-only: initialize predefined templates

## Enhanced Statistics
Base: `/enhanced-stats`

- GET `/overview` — Comprehensive platform overview with relevance, difficulty, and platform distributions
- GET `/algorithm-relevance` — Tag-level relevance analysis (query: `min_problems`)
- GET `/difficulty-calibration` — Difficulty calibration with rating bins per level
- GET `/interview-readiness` — Readiness counts and recommended focus areas
- GET `/quality-improvements` — Summary of dataset quality improvements

Notes:
- These endpoints summarize the live database; values change as data updates.

## Problems & Solutions

- GET `/problems` — List problems with filters: `platform`, `difficulty`, `min_quality`, `min_relevance`, `limit`, `offset`
- GET `/problems/{problem_id}` — Retrieve a single problem
- GET `/problems/{problem_id}/solutions` — List solutions; filters: `min_quality`, `limit`
- GET `/solutions/{solution_id}` — Retrieve a single solution
- GET `/recommendations` — Personalized or basic recommendations; query: `user_id`, `difficulty_level`, `focus_area`, `limit`
- GET `/recommendations/similar/{problem_id}` — Content-based similar problems; query: `limit`
- POST `/ml/train` — Train in-memory recommendation models

## Search & Analytics

- GET `/search` — Simple search across title/description; query: `query`, `limit`
- GET `/search/suggestions` — Typeahead suggestions; query: `partial`
- GET `/analytics/user/{user_id}` — User analytics (query: `days_back`)
- GET `/analytics/trends` — Trending problems and usage (query: `days_back`)
- GET `/analytics/algorithm-tags` — Aggregates by algorithm tags
- GET `/analytics/platforms` — Aggregates by platform
- GET `/analytics/difficulty` — Aggregates by difficulty

## Code Execution

Base: `/execution`

- POST `/run` — Execute code; body: `{ code, language, test_inputs?, timeout_seconds?, memory_limit_mb? }`
- POST `/test` — Run multiple test cases; body: `{ code, language, test_cases[], timeout_seconds? }`
- POST `/analyze` — Execute + analyze with suggestions; body: `{ code, language, problem_type?, custom_test_cases? }`
- GET `/languages` — Supported languages and defaults

## Google Code Analysis

Base: `/google`

- POST `/analyze` — Google-style code analysis; body includes `code`, `language`, optional `problem_id`, `time_spent_seconds`, `thinking_out_loud`, `communication_notes`
- GET `/google-standards` — Evaluation criteria reference
- GET `/complexity-guide` — Time/space complexity reference

## Reading Materials

Base: `/reading-materials`

- GET `/search` — Search materials; query supports `query`, `content_type`, `difficulty_level`, `concept_ids`, `user_id`, `limit`
- GET `/recommendations/{user_id}` — Personalized reading recommendations; query: `context`, `problem_id`, `limit`
- GET `/material/{material_id}` — Fetch a material; query: `user_id`, `include_content`
- POST `/material/{material_id}/progress` — Update reading progress; query: `user_id`; body: `{ progress_percentage, reading_time_seconds, sections_read?, notes?, bookmarked_sections? }`
- POST `/material/{material_id}/rating` — Submit rating/feedback; query: `user_id`; body: `{ user_rating (1-5), difficulty_rating?, usefulness_rating?, feedback_text?, would_recommend? }`
- GET `/collections` — List collections; query: `collection_type`, `difficulty_level`, `target_persona`, `limit`
- GET `/collection/{collection_id}` — Collection with materials; query: `user_id`
- GET `/analytics/{material_id}` — Material analytics; query: `period`
- POST `/recommendation/{recommendation_id}/dismiss` — Dismiss a recommendation; query: `reason?`

## SRS (Spaced Repetition)

Base: `/srs`

- GET `/next` — Next due review cards; query: `limit`, `deck?`
- POST `/review` — Submit a review; body: `{ problem_id, outcome: again|hard|good|easy }`
- GET `/stats` — SRS stats
- GET `/metrics` — SRS metrics; query: `days`
- POST `/retrieval-practice` — Log retrieval practice; body: `{ problem_id, retrieval_type, success_rate (0..1), retrieval_strength (0..1) }`

## Favorites (Bookmarks)

- GET `/favorites` — Query: `user_id`, `include_details?`
- POST `/favorites/toggle` — Body: `{ user_id, problem_id, favorite }`

## Skill Tree Proxy (Expanded Lists)

Base: `/skill-tree-proxy`

- GET `/skill-area/{skill_area}/problems` — Proxies Skill Tree v2; common query: `page`, `page_size`, `sort_by`, `sort_order`, `difficulty?`, `query?`, `platform?`, `title_match?`, `favorites_only?`, `user_id?`
- GET `/tag/{tag}/problems` — Same query as above; optional favorites filtering when `user_id` provided
- GET `/tags/overview` — Proxy of v2 tags overview; query: `top_problems_per_tag` (default 5)
## Skill Tree Optimized (v2)

Base: `/skill-tree-v2`

- GET `/overview-optimized`
    - Query: `user_id` (optional), `top_problems_per_area` (default 5)
    - Returns a lightweight overview by skill areas with difficulty distributions and top problems per area.

- GET `/skill-area/{skill_area}/problems`
    - Query: `page` (default 1), `page_size` (default 20), `difficulty` (optional: Easy|Medium|Hard), `sort_by` (quality|relevance|difficulty|title), `query` (optional, filters by title or tag substring), `platform` (optional: leetcode|codeforces|custom), `title_match` (optional: prefix|exact)
    - Returns paginated problems for a skill area.

- GET `/tags/overview`
    - Query: `top_problems_per_tag` (default 5)
    - Returns a tags overview with counts, difficulty distribution, and top problems per tag.

- GET `/tag/{tag}/problems`
    - Query: `page` (default 1), `page_size` (default 20), `difficulty` (optional: Easy|Medium|Hard), `sort_by` (quality|relevance|difficulty|title), `query` (optional, filters by title or tag substring), `platform` (optional), `title_match` (optional: prefix|exact)
    - Returns paginated problems for a given algorithm tag.

Notes:
- Sorting by `difficulty` orders by Easy→Medium→Hard and within each bucket by sub_difficulty_level (higher first).
- These endpoints are designed for large datasets and avoid returning thousands of records at once.
- Lightweight in-process caching (TTL ~60s) is applied to popular list endpoints to reduce repeated computation during browsing.

Implementation detail:
- Problems include a nullable column `primary_skill_area` to support SQL-side filtering for skill areas. A migration adds this field and a one-time backfill script computes it from `algorithm_tags`. When null, the v2 endpoints fall back to computing the primary skill in Python to maintain correctness during rolling upgrades.
## Notes
- Some endpoints may require specific database records (e.g., valid problem IDs) and will return 404 when not found.
## Examples

These quick examples illustrate common request/response shapes. Replace values as needed.

### POST /ai/hint

Request body
- problem_id: string (must exist in DB)
- query: optional user prompt or question
- session_id: optional to apply per-session hint budgets

Example request
{
    "problem_id": "two_sum_1",
    "query": "Any edge cases to watch?",
    "session_id": "sess-user-123"
}

Example response
{
    "problem_id": "two_sum_1",
    "provider": "local",
    "model": "ollama/llama3:8b-instruct",
    "hints": [
        {"level": "conceptual", "text": "Identify the core pattern first (e.g., arrays/graphs)."},
        {"level": "structural", "text": "Outline inputs/outputs, invariants, and a step plan before coding."},
        {"level": "concrete", "text": "Start with a small example; trace your steps and verify edge cases. Consider: Any edge cases to watch?"}
    ],
    "meta": {"session_id": "sess-user-123", "hints_used": 1}
}

Errors
- 403 when AI is disabled
- 404 when problem not found
- 429 with Retry-After header when rate-limited or budget exceeded

### POST /practice/session

Request body
{
    "size": 5,
    "difficulty": "Medium",
    "focus_areas": ["arrays", "sliding_window"],
    "interleaving": true
}

Example response
{
    "count": 5,
    "interleaving": true,
    "problems": [
        {"id": "p123", "title": "Max Subarray", "difficulty": "Medium", "algorithm_tags": ["arrays", "kadane"], ...},
        {"id": "p456", "title": "Longest K Distinct", "difficulty": "Medium", "algorithm_tags": ["sliding_window"], ...}
    ]
}

Notes
- count may be less than requested if filters are strict

### POST /learning-paths/generate

Request body
{
    "user_profile": {
        "goals": ["google_interview"],
        "current_level": "intermediate",
        "available_weeks": 6,
        "hours_per_week": 8
    },
    "template_id": null
}

Example response (truncated)
{
    "path_id": "lp_abc123",
    "user_id": "default_user",
    "status": "active",
    "weekly_plan": [
        {"week": 1, "topics": ["arrays", "hashing"], "problems": ["p1", "p2"], "milestones": ["m1"]},
        {"week": 2, "topics": ["two_pointers", "sliding_window"], "problems": ["p3", "p4"], "milestones": ["m2"]}
    ],
    "milestones": [{"id": "m1", "title": "Arrays baseline"}, {"id": "m2", "title": "Window mastery"}]
}

Follow-ups
- POST /learning-paths/{path_id}/progress to record completions
- POST /learning-paths/{path_id}/adapt to adjust based on performance

### POST /learning-paths/quick-start

Creates a learning path using opinionated presets for absolute beginners. Designed for minimal input and fast onboarding.

Request body
- user_id: string (optional; defaults to single-user mode user)
- preset_id: string (optional; default beginner preset used when omitted)
- hours_per_week: number (optional; e.g., 5–8)
- duration_weeks: number (optional; e.g., 2–8)
- goals: string[] (optional; examples: ["foundations", "google_interview"])

Example request
{
    "user_id": "default_user",
    "hours_per_week": 5,
    "goals": ["foundations"]
}

Example response (truncated)
{
    "learning_path": {
        "id": "lp_qs_123",
        "user_id": "default_user",
        "target_goal": "foundations",
        "current_level": "beginner",
        "duration_weeks": 4,
        "total_problems": 24,
        "estimated_completion_time": {
            "total_hours": 20,
            "hours_per_week": 5,
            "easy_problems": 12,
            "medium_problems": 10,
            "hard_problems": 2
        },
        "weekly_plan": [
            { "week": 1, "focus_areas": ["arrays", "hashing"], "problems": [/* ... */], "estimated_hours": 5 },
            { "week": 2, "focus_areas": ["two_pointers", "sliding_window"], "problems": [/* ... */], "estimated_hours": 5 }
        ]
    }
}

Notes
- Uses beginner templates defined in the learning path engine; when preset_id is omitted, a default absolute-beginner preset is chosen.
- The response shape mirrors the standard generate endpoint to simplify UI integration.
