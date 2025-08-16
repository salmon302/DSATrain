# Single-User Mode

DSATrain is designed for single-user use out of the box. The system includes some multi-user–capable tables and endpoints for future extensibility, but you do not need to configure accounts.

This page explains how the single user is represented, how to manage your profile and app settings, and where multi-user artifacts appear.

## Identity: the current user

- The application assumes a single logical user. In most places, this user is represented by the string `default_user`.
- Some API endpoints accept a `user_id` for compatibility. In single-user mode you can omit it where optional, or pass `default_user`.

## Managing your profile and settings

There are two related areas to configure:

1) App settings (AI provider, rate limits, budgets, and a light cognitive profile stored in JSON)
2) Learning profile and progress (stored in the database and used by skill tree and practice features)

### App settings

- Endpoint base: `/settings`
- Backing store: `config/user_settings.json`

Key routes:
- `GET /settings` — Returns your settings with API keys masked.
- `PUT /settings` — Update settings. You can change `enable_ai`, `ai_provider`, `model`, rate limits, budgets, and `cognitive_profile`.
- `POST /settings/validate` — Validate a potential update without saving.
- `GET /settings/effective` — Returns runtime-effective flags (e.g., whether provider keys are present via env vars).
- `GET /settings/models` — Suggested model identifiers per provider.

Notes:
- API keys can be provided via environment variables (preferred) or stored in `user_settings.json` (`settings.api_keys`). Keys are masked in responses.
- The `cognitive_profile` nested under settings is a light, local-first profile used for UI and sanity defaults.

### Learning profile and progress

- Backing store: Database tables (SQLite by default; see `dsatrain_phase4.db`).
- Primary models:
  - `UserCognitiveProfile` — cognitive attributes for the user
  - `UserProblemConfidence` — per-problem confidence and attempts
  - `UserSkillMastery` — mastery levels per skill area
  - `UserSkillTreePreferences` — UI visualization preferences

Key API routes touching learning data:
- Skill Tree
  - `GET /skill-tree/overview?user_id=default_user` — Full overview with problems organized by skill area.
  - `POST /skill-tree/confidence?user_id=default_user` — Update confidence for a problem.
  - `GET /skill-tree/user/default_user/progress` — Aggregated progress and mastery.
  - `GET /skill-tree/preferences/default_user` and `POST /skill-tree/preferences/default_user` — Visualization preferences.
- Optimized Skill Tree (lighter payloads)
  - `GET /skill-tree-v2/overview-optimized` — Summary view; designed for single-user/dev use. Returns `user_id` when provided.
  - `GET /skill-tree-v2/tags/overview` — Aggregate problem counts by tag.
- SRS (Spaced Repetition)
  - `GET /srs/next` — Next cards due.
  - `POST /srs/review` — Submit a review result.
  - `GET /srs/stats` and `GET /srs/metrics` — Basic stats and activity metrics.

Notes:
- SRS tables are global in single-user mode (no `user_id`). Skill Tree tables are keyed by `user_id` but you can use `default_user`.
- Some `skill-tree` endpoints accept a `user_id`. In single-user mode, pass `default_user` when required.

## Practical examples

- Update cognitive profile and basic settings:
  - `PUT /settings` with body:
    {
      "enable_ai": true,
      "ai_provider": "anthropic",
      "cognitive_profile": {
        "working_memory_capacity": 7,
        "learning_style_preference": "balanced",
        "visual_vs_verbal": 0.5,
        "processing_speed": "average"
      }
    }

- Check effective settings (no secrets):
  - `GET /settings/effective`

- Record confidence for a problem:
  - `POST /skill-tree/confidence?user_id=default_user`
    {
      "problem_id": "two_sum",
      "confidence_level": 3,
      "solve_time_seconds": 600,
      "hints_used": 0
    }

- View progress summary:
  - `GET /skill-tree/user/default_user/progress`

- Get/Set visualization preferences:
  - `GET /skill-tree/preferences/default_user`
  - `POST /skill-tree/preferences/default_user`
    {
      "preferred_view_mode": "columns",
      "show_confidence_overlay": true,
      "auto_expand_clusters": false,
      "highlight_prerequisites": true,
      "visible_skill_areas": ["array_processing", "string_algorithms"]
    }

## Multi-user notes

- The database schema includes `user_id` in several tables to support potential multi-user scenarios. In single-user deployments, use `default_user` consistently.
- The presence of `user_id` parameters on some endpoints is for compatibility. You can continue using them or omit where optional.

## Where data lives

- Settings (including masked API keys and a lightweight profile): `config/user_settings.json`
- Learning and practice data: SQLite DB (default `sqlite:///./dsatrain_phase4.db`).

## Troubleshooting

- If endpoints reference a `user_id`, use `default_user`.
- If AI features are disabled due to missing keys, check:
  - Environment variables: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`
  - `settings.api_keys` in `config/user_settings.json`
- If you see empty results in Skill Tree, ensure the database is initialized and contains problems with skill tree metadata.
