# 🚀 DSATrain - AI-Powered Interview Preparation Platform

> **Complete AI-Enhanced Coding Interview Preparation with Local-First Privacy**

## 📋 **Overview**

DSATrain is a **comprehensive, AI-powered interview preparation platform** designed for Google-style coding interviews. Featuring advanced AI capabilities, semantic similarity matching, and intelligent recommendations - all while maintaining complete local privacy.

### 🎯 **AI-Enhanced Features**

- **🧠 AI-Powered Recommendations**: Semantic embeddings with 128-dimensional problem matching
- **📊 Multi-Dimensional Difficulty**: 5-dimensional complexity analysis for optimal progression
- **⭐ Quality-Based Curation**: Google interview relevance scoring with academic standards
- **🎯 Adaptive Learning Paths**: 52-concept knowledge graph with prerequisite tracking
- **🤖 Behavioral Interview AI**: Complete conversation frameworks with STAR method evaluation
- **📈 Predictive Analytics**: Performance forecasting and weakness identification
- **🔒 Privacy-First**: All AI processing and data storage completely local

## 🏗️ **Advanced AI Architecture** 

- **Backend**: FastAPI with AI-enhanced endpoints and machine learning integration
- **Frontend**: React + TypeScript with intelligent user interfaces
- **Database**: SQLite with 10,618+ problems featuring complete AI enhancement (480+ AI features)
- **AI Features**: 10 specialized database tables for embeddings, difficulty vectors, and concept graphs
- **Data Pipeline**: Automated processing with real-time quality monitoring
- **File Organization**: Clean root directory with comprehensive AI framework

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- Git

### **Windows one-time setup**
1) Create and activate a virtual environment (first run only):
	 - cmd.exe
		 - python -m venv .venv
		 - .\.venv\Scripts\activate
	 - PowerShell
		 - python -m venv .venv
		 - .venv\Scripts\Activate.ps1

2) Install backend deps: pip install -r requirements.txt
3) Install frontend deps: cd frontend && npm install && cd ..

After that, you can use the launch scripts below.

### **Launch options (Windows)**
- One-click: double-click `launch_dsatrain.bat` (starts backend, skill-tree server, and frontend)
- Dev mode: double-click `launch_dsatrain_dev.bat` (adds pre-checks and extra logs)

Or run manually in two terminals:
- Terminal A (backend):
	- .\.venv\Scripts\activate && python -m uvicorn src.api.main:app --reload --port 8000
- Terminal B (frontend):
	- cd frontend && npm start

### **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Skill Tree API**: http://localhost:8000/skill-tree (v1) and http://localhost:8000/skill-tree-v2 (v2 via proxy)

Tip: Skill Tree v1 and v2 are mounted on the main backend by default. The frontend fetches v2 lists via `/skill-tree-proxy/*` on the main API. To run an external skill-tree service (e.g., on port 8002), set `REACT_APP_SKILL_TREE_URL` and `REACT_APP_FEATURE_SKILL_TREE_MAIN_API=off` in `frontend/.env`, or point `SKILL_TREE_V2_URL` on the backend to the external URL.

### Skill Tree configuration

- REACT_APP_FEATURE_SKILL_TREE_MAIN_API: on by default. When `off` and `REACT_APP_SKILL_TREE_URL` is set, the frontend calls the external Skill Tree service directly.
- REACT_APP_SKILL_TREE_URL: Optional. Base URL of an external Skill Tree service (e.g., http://localhost:8002). Used only when the feature flag above is `off`.
- SKILL_TREE_V2_URL: Backend env var. Defaults to `http://localhost:8000/skill-tree-v2` (this instance). Set to an external service base to have `/skill-tree-proxy/*` proxy to a different process.

## 📊 **Current Status**

✅ **Complete AI Framework**: Production-ready intelligent interview platform  
- **10,618 Problems** with semantic embeddings and quality scoring
- **480+ AI Features** across 4 enhancement dimensions  
- **52-Concept Knowledge Graph** with prerequisite relationships
- **Behavioral Interview Framework** with conversation templates
- **Real-time Pipeline** with automated quality monitoring
- **Academic-Grade Evaluation** using research-based heuristics

🚀 **AI-Powered Platform Ready**: Advanced features deployed  
- Semantic similarity search for intelligent problem recommendations
- Multi-dimensional difficulty assessment for adaptive learning
- Quality-based content curation with Google interview relevance
- Behavioral competency framework with STAR method evaluation
- Automated data pipeline with excellent health monitoring

## 📁 **AI-Enhanced Project Structure**

```
DSATrain/ (AI-Powered Platform)
├── 📄 README.md                # Project overview
├── 📄 dsatrain_phase4.db       # SQLite database (10,618+ problems + AI features)  
├── 📄 launch_dsatrain.bat      # One-click launcher
├── 📁 src/                     # FastAPI backend with AI integration
│   ├── api/                    # REST endpoints + AI APIs
│   ├── ml/                     # AI feature engineering + similarity engine
│   ├── models/                 # Database models + AI features models
│   ├── processors/             # Data processing + AI pipeline
│   └── services/               # Business logic + AI services
├── 📁 frontend/                # React TypeScript with AI features
├── 📁 data/                    # Comprehensive datasets + AI features
│   ├── processed/              # Unified data + AI embeddings
│   ├── expert_labeled/         # Professional evaluation frameworks  
│   └── synthetic/              # AI-generated training data
├── 📁 tests/                   # Test suite with AI validation
├── 📁 docs/                    # Complete documentation + AI implementation plans
├── 📁 alembic/                 # Database migrations + AI features
└── 📁 archive/                 # Legacy components preserved
```

## 🧪 **Testing**

```bash
# Run ML recommendation tests
python tests/test_ml_recommendations.py

# Run all tests
python -m pytest tests/
```

Optional external API tests (skipped by default): Enable tests that hit live servers by setting an environment variable.

Windows PowerShell
```powershell
$env:RUN_EXTERNAL_API_TESTS = "1"; pytest -q
Remove-Item Env:RUN_EXTERNAL_API_TESTS
```

Use an in-memory DB for isolated test runs (optional):

```powershell
$env:DSATRAIN_DATABASE_URL = 'sqlite:///:memory:'; pytest -q
Remove-Item Env:DSATRAIN_DATABASE_URL
```

## 📊 **AI Platform Capabilities**

- ✅ **10,618 AI-Enhanced Problems** with semantic embeddings and quality scoring
- ✅ **480+ AI Features** including embeddings, difficulty vectors, and concept graphs
- ✅ **52-Concept Knowledge Graph** with prerequisite relationships and learning paths
- ✅ **Behavioral Interview Framework** with 4-tier competency taxonomy
- ✅ **Academic Quality Engine** with 9 research-based evaluation criteria
- ✅ **Real-Time Data Pipeline** with automated monitoring and quality assurance
- ✅ **Production-Ready Database** with 10 AI-specific tables and optimized queries

## 🎯 **API Endpoints (Implemented)**

- **Health & Ops**
  - `GET /` — Basic service info
  - `GET /health` — Health check with DB probe

- **Settings**
  - `GET /settings` — Current settings (query: `include_providers`, `include_effective_flags`)
  - `PUT /settings` — Update settings
  - `POST /settings/cognitive-profile` — Update cognitive profile
  - `GET /settings/providers` — Allowed AI providers + notes
  - `GET /settings/effective` — Effective settings (no secrets)
  - `POST /settings/validate` — Validate without saving
  - `GET /settings/models` — Suggested models; optional `provider`

- **Problems & Recommendations**
  - `GET /problems` — Filters: `platform`, `difficulty`, `min_quality`, `min_relevance`, `limit`, `offset`
  - `GET /problems/{problem_id}` — Single problem
  - `GET /problems/{problem_id}/solutions` — Problem solutions
  - `GET /solutions/{solution_id}` — Single solution
  - `GET /recommendations` — Personalized/basic recommendations
  - `GET /recommendations/similar/{problem_id}` — Similar problems
  - `POST /ml/train` — Train in-memory recommendation models

- **Search & Analytics**
  - `GET /search` — Problem search; see also `/search/suggestions`
  - `GET /search/suggestions` — Typeahead suggestions
  - `POST /interactions/track` — Track user interactions
  - `GET /analytics/user/{user_id}` — User analytics
  - `GET /analytics/trends` — Trends
  - `GET /analytics/algorithm-tags` — Tag analytics
  - `GET /analytics/platforms` — Platform analytics
  - `GET /analytics/difficulty` — Difficulty analytics

- **Learning Paths**
  - `GET /learning-paths/templates`
  - `GET /learning-paths/templates/recommendations`
  - `POST /learning-paths/generate` — Generate personalized path
  - `GET /learning-paths/{path_id}`
  - `GET /learning-paths/{path_id}/next-problems`
  - `POST /learning-paths/{path_id}/progress`
  - `POST /learning-paths/{path_id}/adapt`
  - `GET /learning-paths/user/{user_id}`
  - `GET /learning-paths/{path_id}/milestones`
  - `POST /learning-paths/{path_id}/milestones/{milestone_id}/complete`
  - `GET /learning-paths/analytics/overview`
  - `POST /learning-paths/admin/initialize-templates`

- **Practice**
  - `POST /practice/session`
  - `POST /practice/attempt`
  - `POST /practice/elaborative`
  - `POST /practice/working-memory-check`
  - `POST /practice/gates/start`
  - `POST /practice/gates/progress`
  - `GET /practice/gates/status`
  - `GET /practice/gates`
  - `GET /practice/gates/{session_id}`
  - `DELETE /practice/gates/{session_id}`

- **SRS**
  - `GET /srs/next`
  - `POST /srs/review`
  - `GET /srs/stats`
  - `GET /srs/metrics`
  - `POST /srs/retrieval-practice`

- **Interview**
  - `POST /interview/start`
  - `POST /interview/complete`

- **Cognitive**
  - `GET /cognitive/profile`
  - `POST /cognitive/assess`
  - `GET /cognitive/adaptation`

- **AI**
  - `POST /ai/hint`
  - `POST /ai/review`
  - `POST /ai/elaborate`
  - `GET /ai/status`
  - `POST /ai/reset`

- **Code Execution** (Base: `/execution`)
  - `POST /execution/run`
  - `POST /execution/test`
  - `POST /execution/analyze`
  - `GET /execution/languages`

- **Google Code Analysis** (Base: `/google`)
  - `POST /google/analyze`
  - `GET /google/google-standards`
  - `GET /google/complexity-guide`

- **Reading Materials** (Base: `/reading-materials`)
  - `GET /reading-materials/search`
  - `GET /reading-materials/recommendations/{user_id}`
  - `GET /reading-materials/material/{material_id}`
  - `POST /reading-materials/material/{material_id}/progress`
  - `POST /reading-materials/material/{material_id}/rating`
  - `GET /reading-materials/collections`
  - `GET /reading-materials/collection/{collection_id}`
  - `GET /reading-materials/analytics/{material_id}`
  - `POST /reading-materials/recommendation/{recommendation_id}/dismiss`

- **Favorites & Skill Tree Proxy**
  - `GET /favorites`, `POST /favorites/toggle`
  - `GET /skill-tree-proxy/skill-area/{skill_area}/problems`
  - `GET /skill-tree-proxy/tag/{tag}/problems`

## 🔧 **Development**

### **Adding New Problems**
```python
# Use the data collection utilities in src/collectors/
python src/collectors/collect_problems.py
```

### **Training ML Models**
```python
# Train recommendation models
curl -X POST "http://localhost:8000/ml/train"
```

### **Database Migrations**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### **Configuration: Database URL overrides**

The backend reads the database URL in this order:

1. Explicit argument passed to `DatabaseConfig`
2. `DSATRAIN_DATABASE_URL` environment variable
3. `DATABASE_URL` environment variable
4. Fallback: `sqlite:///./dsatrain_phase4.db`

Windows PowerShell examples:

```powershell
# Use a separate on-disk DB during development
$env:DSATRAIN_DATABASE_URL = 'sqlite:///./dsatrain_phase4_dev.db'; python -m uvicorn src.api.main:app --reload

# Switch to an in-memory DB for quick experiments
$env:DSATRAIN_DATABASE_URL = 'sqlite:///:memory:'; python -m uvicorn src.api.main:app --reload

# Clear the override
Remove-Item Env:DSATRAIN_DATABASE_URL
```

### Settings & API reference

- Settings endpoints summary: `/settings`, `/settings/providers`, `/settings/effective`, `/settings/validate` (PUT/POST)
- Full, maintained list of endpoints with methods and brief descriptions: see `docs/API_REFERENCE.md`

### **Settings & AI Providers**

Allowed `ai_provider` values: `openai`, `anthropic`, `openrouter`, `local`, `none`.

- Use `/settings/providers` to retrieve the allowed list plus quick notes for the UI.
- Use `/settings/effective` to retrieve a secrets-safe effective view with `api_keys_present` flags.
- You can also inline extras via GET `/settings`:
	- `?include_providers=true` to include allowed providers + notes
	- `?include_effective_flags=true` to include `api_keys_present`
- Supply API keys via either:
	- Environment variables: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY` (recommended for local dev)
	- Or write them via `PUT /settings` under `api_keys` (keys are masked in GET /settings)
- Clearing a key: send `"api_keys": {"openai": null}` to `PUT /settings`.
- Env keys are merged into GET `/settings` but are not persisted to disk.

#### Validate settings without saving

- Use `POST /settings/validate` to check if a proposed settings change would be valid and ready before persisting.
- Request body: same shape as `PUT /settings` (any subset of fields).
- Behavior:
	- Considers environment variables and keys provided in the request body.
	- Ignores previously persisted keys when validating (safe for preflight checks).
	- Does not write anything to disk.
- Responses:
	- 200 OK (valid): returns `valid: true` plus readiness flags
	- 400 Bad Request (invalid): returns `detail.errors` array plus readiness flags to help the UI
### AI endpoints and throttling

- `POST /ai/hint` — Returns conceptual/structural/concrete hints for a problem ID.
- `POST /ai/review` — Heuristic code review (no external calls).
- `POST /ai/elaborate` — “Why/How” question prompts for deeper thinking.
- `GET /ai/status` — Returns current AI enablement, provider/model, and rate-limit usage:
	- enabled, provider, model
	- rate_limit_per_minute, rate_limit_used, rate_limit_window_seconds
	- hint_budget_per_session, hints_used_this_session (when session_id provided)

- `POST /ai/reset` — Reset in-memory AI counters. Useful in development/tests:
	- Body: `{ "session_id": "optional-session", "reset_global": true }`
	- When `reset_global` is true (default), clears the global rate limiter bucket.
	- When `session_id` is provided, clears that session's hint usage.
	- Returns the current `/ai/status` payload after reset.

Throttling behavior:
- Global rate limit per minute is configured via `rate_limit_per_minute` in settings.
- Rate limit window size is configured via `rate_limit_window_seconds` (min 10s, max 3600s). Retry-After is computed based on this window.
- Per-session hint budget is configured via `hint_budget_per_session` (enforced only when a valid hint is served).
- When the global rate limit is exceeded, requests return HTTP 429 with a `Retry-After` header indicating seconds until retry is safe.
- When AI is disabled or provider is `none`, requests return HTTP 403.

Windows PowerShell examples:

```powershell
# Set a small rate limit and window, then reset counters
Invoke-RestMethod -Method Put -Uri http://localhost:8000/settings -ContentType 'application/json' -Body '{
	"enable_ai": true,
	"ai_provider": "local",
	"model": "ollama/llama3:8b-instruct",
	"rate_limit_per_minute": 2,
	"rate_limit_window_seconds": 10
}'

# Check status
Invoke-RestMethod -Method Get -Uri http://localhost:8000/ai/status | ConvertTo-Json -Depth 5

# Reset global bucket
Invoke-RestMethod -Method Post -Uri http://localhost:8000/ai/reset -ContentType 'application/json' -Body '{"reset_global": true}'
```

### Optional: Redis-backed rate limiting (horizontal-ready)

By default, DSATrain uses an in-memory rate limiter and hint budget counters. You can optionally enable a Redis-backed limiter to share counters across processes or containers.

Requirements:
- A reachable Redis server (local or remote)
- The Python package `redis` installed in your environment

Enable on Windows (cmd.exe):

```cmd
REM Install the Redis client package if needed
pip install redis

REM Point to your Redis server (default shown) and enable Redis-backed limiter
set DSATRAIN_REDIS_URL=redis://localhost:6379/0
set DSATRAIN_USE_REDIS_RATE_LIMIT=1

REM Run the backend (example)
python -m uvicorn src.api.main:app --reload
```

Notes:
- If Redis is unreachable or the `redis` package isn’t installed, the service gracefully falls back to in-memory limiting.
- The `/ai/reset` endpoint clears both the global bucket and per-session hint budgets in Redis when enabled.
- Recommended for multi-worker or multi-instance deployments.

### Optional: Cache serialization mode (security vs compatibility)

Redis caching supports two serialization modes for values:

- pickle (default): Maximum compatibility with Python objects but higher risk if Redis is compromised.
- json: Safer (no code execution), but only caches JSON-serializable data (primitives, lists, dicts).

Configure via environment variable (cmd.exe):

```cmd
REM Safer JSON mode (recommended for stricter environments)
set DSATRAIN_CACHE_SERIALIZATION=json

REM Default (compatible but riskier)
set DSATRAIN_CACHE_SERIALIZATION=pickle
```

When in JSON mode, non-JSON-serializable results will be cached only in memory and skipped for Redis.
The current mode and cache status are visible in `GET /health` under `cache.serialization`.

## 📚 **Documentation**

- **Data Framework**: `docs/DATA_FRAMEWORK_GAPS_ANALYSIS.md` - Complete implementation status
- **AI Implementation**: `docs/AI_IMPLEMENTATION_PLAN.md` - AI features and roadmap
- **Project Status**: `docs/CURRENT_PROJECT_STATUS.md` - Current development state
- **Database Development**: `docs/DATABASE_DEVELOPMENT_PRIORITIES.md` - Database features
- **Single-User Mode**: `docs/single_user_mode.md` - How identity works (default_user) and how to manage your profile and settings
- **API Documentation**: Available at `/docs` when running backend
- **Frontend Guide**: `frontend/README.md`

### New: Favorites and Skill Tree → Practice

- You can now favorite problems. Click the bookmark icon on Skill Tree cards or in the Practice header. Favorites are stored per user and available via `GET /favorites`.
- From the Skill Tree, use the play icon on a problem to jump directly into the Code Practice editor with that problem preloaded.

## 🧪 Try It (Service Wrappers)

Below are minimal examples using the frontend TypeScript service wrappers. Ensure `REACT_APP_API_URL` points to your backend (default is `http://localhost:8000`). See `docs/API_REFERENCE.md` for full details.

```ts
// AI status via wrapper
import { aiAPI } from './frontend/src/services/api';

async function checkAI() {
  const status = await aiAPI.getStatus();
  console.log('AI status:', status);
}

// Practice session via wrapper
import { practiceAPI, getCurrentUserId } from './frontend/src/services/api';

async function startPractice() {
  const userId = getCurrentUserId();
  const session = await practiceAPI.startSession({ user_id: userId, size: 3 });
  console.log('Practice session:', session);
}
```

See maintained endpoint list in [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md).

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 **Acknowledgments**

- Built with cutting-edge AI technologies and machine learning best practices
- Advanced data framework powered by academic research and Google documentation
- Comprehensive datasets from Codeforces, HackerRank, university resources, and academic papers
- AI features including semantic embeddings, concept graphs, and behavioral evaluation frameworks
- Production-ready platform suitable for serious interview preparation

---

**Master Your Interviews with AI! 🚀**

