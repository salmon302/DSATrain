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
