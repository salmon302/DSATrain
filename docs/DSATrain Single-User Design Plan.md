## DSATrain Single-User Redesign Plan

### Vision

Build a personal DSA training app that maximizes educational value through a structured learning system grounded in cognitive science, aligned with Google-style interviewing, and powered by optional AI assistance using the user’s API key.

### Goals

- **DSA mastery**: Foundation → patterns → application with deliberate practice and spaced repetition.
- **Interview readiness**: Timed practice, communication, rubric-aligned reviews for Google criteria (GCA, RRK, communication).
- **Personalization**: Single-user data, customizable sessions, provider-agnostic AI with strict privacy and cost controls.
- **Discoverability and progress**: Rich problem catalog, granular difficulty, priorities, and transparent analytics.

### Scope and Principles

- **Single process**: One FastAPI backend with SQLite; React frontend. No multi-server variants.
- **Local-first**: Store personal data locally; user-provided AI keys stored locally only.
- **Cognitive design**: Productive struggle, interleaving, chunking, SRS, and reflective practice.
- **Low friction**: Simple setup, clear flows, sensible defaults, export/import of progress.

### Keep, Refactor, Archive

- **Keep and refactor**
  - Backend FastAPI: `src/api/main.py`, routers `learning_paths.py`, `google_code_analysis.py`, `code_execution.py`, `enhanced_stats.py`.
  - Models: `src/models/database.py` (Problems, LearningPath, UserLearningPath, UserInteraction) with extensions.
  - Engines: `src/ml/recommendation_engine.py`, `src/ml/learning_path_engine.py` (adapt for single-user signals).
  - Frontend: `frontend/src` core pages and components; `GoogleStyleCodeEditor.tsx`, `SkillTreeVisualization.tsx`.
  - Data: `data/` curated datasets and essential import/migration utilities.

### Architecture Overview

- **Backend (FastAPI, SQLite)**
  - ProblemCatalogService: rich filtering, tagging, discovery, dual-coding content management.
  - PracticeEngine: builds sessions with interleaving, difficulty curves, and gating (dry run → pseudocode → code).
  - SRSService: review scheduling (Anki-like) over problems/patterns with retrieval practice variants.
  - InterviewService: timed sessions, Google rubric scoring, comms prompts, post-mortems.
  - AIService: provider-agnostic adapters (OpenAI/Anthropic/OpenRouter/local), hint/review policies, rate/cost controls.
  - AnalyticsService: attempts, time-on-task, error types, insights.
  - CognitiveService: working memory assessment, learning style adaptation, elaborative interrogation.
  - RetrievalEngine: low-stakes testing, memory consolidation, transfer assessment.
- **Frontend (React TS)**
  - Pages: Dashboard, Problem Browser, Practice, Review (SRS), Interview, Learning Paths, Settings.
  - Components: Gated code editor with Socratic hints and rubric feedback; session builder; analytics widgets.

### Data Model Extensions (SQLite)

- **Problem** (extend existing):
  - `pattern_tags: JSON`, `skill_areas: JSON`, `granular_difficulty: Integer (1–5)`
  - `interview_frequency: Float`, `company_tags: JSON`, `google_interview_relevance: Float`
  - `source_dataset: String`, `canonical_solutions: JSON`
  - `visual_aids: JSON`, `verbal_explanations: JSON`, `prerequisite_assessment: JSON`
  - `elaborative_prompts: JSON`, `working_memory_load: Integer (1-10)`
- **New tables**
  - `ReviewCard(problem_id, next_review_at, interval_days, ease, reps, lapses, last_outcome, deck)`
  - `ReviewHistory(problem_id, outcome, time_spent, notes, timestamp)`
  - `ProblemAttempt(problem_id, code, language, status, time_spent, test_results, mistakes, reflection, created_at)`
  - `UserCognitiveProfile(user_id, working_memory_capacity, learning_style_preference, visual_vs_verbal, processing_speed)`
  - `ElaborativeSession(problem_id, why_questions, how_questions, responses, timestamp)`
  - `RetrievalPractice(problem_id, retrieval_type, success_rate, retrieval_strength, timestamp)`

### API Surface (initial)

- **Settings**
  - `GET /settings` – read local settings (AI provider, caps, cognitive preferences)
  - `PUT /settings` – update settings; validate API key with a test call
  - `POST /settings/cognitive-profile` – assess and update cognitive preferences
- **Catalog**
  - `GET /problems` – filters: difficulty, granular_difficulty, patterns, skills, companies, relevance, acceptance, working_memory_load
  - `GET /problems/{id}` – details with canonical metadata, visual aids, elaborative prompts
  - `GET /problems/{id}/dual-coding` – visual and verbal representations
  - `GET /search` – full-text/pattern search with cognitive load filtering
- **Practice**
  - `POST /practice/session` – generate session (size, interleaving, targets, cognitive adaptation)
  - `POST /practice/attempt` – save attempt and reflection
  - `POST /practice/elaborative` – guided why/how question session
  - `POST /practice/working-memory-check` – assess cognitive load during problem solving
- **SRS**
  - `GET /srs/next` – due reviews with retrieval practice variants
  - `POST /srs/review` – record review outcome
  - `GET /srs/stats` – review metrics
  - `POST /srs/retrieval-practice` – low-stakes retrieval without full problem solving
- **Interview**
  - `POST /interview/start` – timed session
  - `POST /interview/complete` – rubric summary and post-mortem
- **AI**
  - `POST /ai/hint` – Socratic, layered hints adapted to learning style
  - `POST /ai/review` – rubric-based narrative review
  - `POST /ai/elaborate` – generate why/how questions for deeper understanding
- **Cognitive**
  - `GET /cognitive/profile` – get user's cognitive learning profile
  - `POST /cognitive/assess` – working memory and learning style assessment
  - `GET /cognitive/adaptation` – get personalized learning recommendations

### AI Integration

- **Provider abstraction**: adapters for OpenAI/Anthropic/OpenRouter/local; pluggable prompt policies.
- **Policies**: layered hints (conceptual → structural → concrete), rubric-aligned reviews, targeted remediation snippets.
- **Controls**: local key storage, rate limiting, monthly cost caps, hint budget per session.

### Educational Workflow

- **Deliberate practice**: clear goal per session, productive struggle timeboxes, reflection logging, delta vs optimal solution.
- **Interleaving**: mix patterns to train pattern discrimination; optional blocked practice when learning new pattern.
- **Chunking scaffolds**: e.g., DP = define states → recurrence → base cases; visible checklists.
- **Spaced repetition**: review learned problems by re-deriving approaches before code; adjustable ease.
- **Think Twice, Code Once**: dry-run and pseudocode gates before editor unlock (overrideable).
- **Interview simulation**: timed flow, communication prompts, Google rubric breakdown.
- **Elaborative interrogation**: guided "why" and "how" questioning for deeper understanding.
- **Dual coding**: visual diagrams + verbal explanations for enhanced comprehension.
- **Retrieval practice**: frequent low-stakes recall without full problem solving.
- **Cognitive load adaptation**: dynamic difficulty adjustment based on working memory capacity.
- **Transfer testing**: novel problem variations to assess pattern recognition strength.

### Dataset Organization and Discovery

- **Catalog**: unify LeetCode/Codeforces/curated lists; retain acceptance, frequency, company tags, Google relevance.
- **Granularity**: difficulty + `granular_difficulty`, `pattern_tags`, `skill_areas`, frequency.
- **Discovery**: multi-filter search, saved views, “build learning path from search”.
- **Import/Update**: retain migration/import utilities; user can import custom CSV/JSON with simple mapping.

### Cognitive Science Implementation Strategy

- **Elaborative Interrogation Engine**:
  - AI-generated "why" and "how" questions tailored to each problem
  - Progressive questioning depth (surface → mechanism → principles)
  - User response tracking for comprehension assessment
  - Integration with hint system for adaptive questioning

- **Dual Coding Content System**:
  - Visual algorithm animations and data structure diagrams
  - Synchronized verbal explanations with visual elements
  - User preference detection (visual vs. verbal learning style)
  - Adaptive content presentation based on cognitive profile

- **Enhanced Retrieval Practice**:
  - Micro-retrieval sessions (pattern identification without full solving)
  - Concept mapping exercises (connect related algorithms/patterns)
  - Explanation generation tasks (teach-back without coding)
  - Frequency tuning based on retrieval strength assessment

- **Working Memory Adaptation**:
  - Real-time cognitive load assessment during problem solving
  - Dynamic problem complexity adjustment
  - Chunking assistance (break complex problems into cognitive units)
  - Scaffolding removal as expertise develops

- **Individual Differences Accommodation**:
  - Processing speed assessment and session pacing
  - Visual vs. verbal learning style adaptation
  - Prior knowledge assessment and prerequisite routing
  - Personalized difficulty curves based on cognitive capacity

### Migration and Immediate Actions

- **Consolidate**: single FastAPI app in `src/api/main.py`; include all routers; remove Flask servers and agentic prototypes.
- **Models**: extend `src/models/database.py` with new fields and tables; create Alembic migrations.
- **Services**: add `src/api/ai.py`, `src/api/srs.py`, `src/api/practice.py`, `src/api/cognitive.py`; `src/services/ai_service.py`, `src/services/srs_service.py`, `src/services/practice_engine.py`, `src/services/cognitive_service.py`.
- **Frontend**: add pages `Review.tsx`, `Practice.tsx`, `Settings.tsx`, `CognitiveAssessment.tsx`; add services for new endpoints; consolidate `.tsx` only.
- **Config**: `.env`-driven API base URLs; local `settings.json` for AI provider, caps, and cognitive preferences.

### Milestones

- **Phase 1: Consolidation & Settings (2–3 days)**
  - Single server, settings endpoints, key validation, cognitive profile setup.
- **Phase 2: Catalog & Data Model (3–4 days)**
  - Problem fields, filters, import refresh, Problem Browser, dual-coding content.
- **Phase 3: SRS Core (3 days)**
  - Scheduler, `/srs/*` endpoints, Review page MVP, retrieval practice variants.
- **Phase 4: Practice Engine + Gated Editor (4–5 days)**
  - Session builder, gated flow, attempts/reflections, elaborative interrogation.
- **Phase 5: AI Layer (4 days)**
  - Adapters, hint policy, rubric review, cost guards, cognitive adaptation.
- **Phase 6: Interview Simulator (3 days)**
  - Timed flow, comms prompts, rubric UI.
- **Phase 7: Cognitive Services (4 days)**
  - Working memory assessment, learning style detection, adaptive content delivery.
- **Phase 8: Analytics & Polish (3 days)**
  - Weak-area insights, saved views, import/export, docs, cognitive metrics.

### Risks and Mitigations

- **LLM dependency and costs**: default to offline heuristics; enforce caps and hint budgets.
- **Data quality variance**: prioritize curated lists; add user feedback and tagging.
- **Scope creep**: milestone gates; ship MVP of each module before enhancements.

### Open Questions

- Preferred AI provider(s) and default model?
- Strength of gating (soft vs strict) for dry-run/pseudocode?
- Default practice session size and interleaving level?
- Priority companies/tags to emphasize in catalog?

### Deliverables

- Single-user app with: rich catalog and filters, guided practice with cognitive scaffolds, SRS reviews with retrieval practice variants, interview simulator with Google rubric, personal analytics, elaborative interrogation engine, dual-coding content system, working memory adaptation, and import/export of progress.

### Enhanced Cognitive Features

- **Elaborative Interrogation**: AI-powered "why" and "how" questioning for deeper understanding
- **Dual Coding Content**: Visual and verbal learning representations with adaptive delivery
- **Enhanced Testing Effect**: Multiple retrieval practice variants beyond traditional SRS
- **Working Memory Adaptation**: Real-time cognitive load monitoring and difficulty adjustment
- **Individual Differences**: Learning style detection and personalized content adaptation
- **Cognitive Analytics**: Comprehensive tracking of cognitive load, learning efficiency, and adaptation effectiveness

// ... existing code ...

### Research-Grounded Iteration

#### 1) Database Expansion Strategy (from Google Interview AI Data Research)

- **Phase 1 – Low-risk ingestion (enable immediate value)**
  - Ingest static Kaggle snapshots of LeetCode problems/solutions with company tags; map to our canonical `Problem` fields (`company_tags`, `google_interview_relevance`, `pattern_tags`, `skill_areas`).
  - Integrate official Codeforces API to pull problems, tags, and acceptance stats; attach `source_dataset` and maintain provenance per record.
  - Enrichments: compute `granular_difficulty` (1–5), `interview_frequency` (from tags/frequency proxies), and `pattern_tags` via our analyzer. Seed SRS decks from curated lists (NeetCode 150, Blind 75).
  - Deduplication: normalize titles, platform IDs, and use fuzzy matching across sources; maintain a `dataset_registry` table for provenance and freshness.
- **Phase 2 – Resilient, ethical pipelines**
  - Build a rate-limited, headless-browser scraper for LeetCode (private, internal use), with change-detection and fallback to unofficial APIs; optional user-permissioned access (bring-your-own-session) for personal data.
  - Acquire public behavioral/system-design corpora (Reddit threads, university question banks) with robust PII anonymization.
  - Begin partner outreach for commercial APIs (e.g., HackerRank for Work) where feasible.
- **Phase 3 – Proprietary data assets**
  - Synthetic generation (Evol-Instruct) for novel problems and variations; curate with expert review.
  - Commission small, expert-labeled STAR datasets to calibrate behavioral scoring.
  - Optional OAuth connectors (e.g., LeetCode/GitHub) for personal history import; strictly local use.
- **Storage & operations**
  - SQLite with indices on (`platform`, `difficulty`), (`quality_score`, `google_interview_relevance`), tags; add `dataset_registry` and ETL job logs.
  - Scheduled refresh jobs (manual trigger initially) and integrity checks; metrics on coverage and staleness.

#### 2) Google Interview Educational Fidelity (from Hiring Process report)

- **Coding interview realism**
  - Plain-text editor mode (no autocomplete); optional “Google Doc” constraint preset.
  - Require candidate-written test cases (OA parity); timeboxed rounds (30–45 min).
  - Enforce the clarify → plan (brute-force first) → optimize → implement → test protocol with UI checklists.
  - Scoring mapped to Google rubric (1–4) across Algorithms/DSA, Coding, Communication, Problem-Solving; store structured scorecards.
  - Problem sampling weighted to Google-tagged, medium/hard, high-frequency topics; interleave arrays/strings, graphs, DP, trees.
- **System design simulation**
  - Knowledge-graph-guided interviewer: prompt sequences covering requirements, high-level design, deep dives, scale/bottlenecks, reliability.
  - Diagram sandbox integration and rubric for depth, trade-offs, scalability, and reliability.
  - Seed scenario bank from curated system-design lists; configurable difficulty and scope.
- **Behavioral/Googleyness**
  - Competency-tagged question bank; STAR scaffolding and evaluator; rubric emphasizing ownership, specificity, quantification, humility/collaboration.
  - Feedback tied to rubric gaps with targeted practice prompts and micro-lessons.

#### 3) Efficient DSA Learning (from Mastering DSA framework)

- **Deliberate practice**
  - Session templates with explicit goals and productive struggle timeboxes; reflection prompts capturing error taxonomy (off-by-one, state mismanagement, complexity misestimation, etc.).
  - “Think Twice, Code Once” gates (problem dry-run notebook → pseudocode → editor unlock) with override logging.
- **Interleaving and pattern discrimination**
  - Toggle between blocked (when first learning a pattern) and interleaved sessions (for transfer). Track misclassification of pattern as a metric.
- **Spaced repetition (SRS)**
  - Default intervals: 1d, 3–4d, 8–10d, 2–3w, 1–2m, then doubling; failures reset interval and decrease ease.
  - Deck types: Problems, Patterns, and “Concept Chunks” (e.g., DP steps). Retrieval-first UI (explain approach before code).
- **Chunking & scaffolds**
  - Built-in checklists for DP (states/recurrence/base cases), graphs (representation/traversal/path/cycle), trees (traversal/invariants), arrays/strings (window/two-pointers/prefix sums).
- **Progress & mastery**
  - Mastery criteria per pattern: accuracy ≥90%, median solve time thresholds, and ability to verbally explain invariants/trade-offs.

#### 4) Advanced Cognitive Science Integration

- **Elaborative interrogation**
  - Progressive questioning engine: surface → mechanism → principle depth levels
  - AI-generated "why" and "how" questions tailored to user level and problem context
  - Comprehension assessment through response analysis and follow-up questioning
- **Dual coding theory**
  - Visual algorithm animations synchronized with verbal explanations
  - Adaptive content delivery based on detected learning style preferences
  - Interactive diagrams for data structures and algorithmic processes
- **Enhanced testing effect**
  - Multiple retrieval practice variants: micro-retrieval, concept mapping, explanation generation
  - Dynamic scheduling based on retrieval strength and problem mastery
  - Low-stakes testing integrated into learning progression
- **Working memory adaptation**
  - Real-time cognitive load monitoring through interaction pattern analysis
  - Dynamic difficulty adjustment based on cognitive capacity assessment
  - Chunking assistance and scaffolding adapted to individual working memory limits
- **Individual differences accommodation**
  - Learning style detection from interaction patterns (visual/verbal/kinesthetic preferences)
  - Processing speed assessment and personalized pacing
  - Prior knowledge assessment and prerequisite skill routing

#### KPIs and Validation

- **Interview fidelity**: rubric score stability across sessions; time-to-first-correct; test-case coverage created by user; adherence to protocol steps.
- **Learning efficiency**: retention rate on SRS reviews, transfer success on novel problems, pattern discrimination accuracy, reduction in typical error categories.
- **Catalog coverage**: % of Google-tagged problems represented, freshness lag, enrichment completeness (patterns/skills/frequency filled).

#### Concrete Implementation Additions

- **New endpoints**
  - `/interview/modes/coding/start|submit`, enforcing no-IDE and requiring user tests.
  - `/interview/modes/system-design/start|submit`, returning rubric and follow-up prompts.
  - `/behavioral/question|submit`, STAR evaluator with rubric output.
- **Frontend**
  - Editor “Google mode”, test-case composer, protocol checklists, STAR coach, system-design canvas.
- **Data**
  - `dataset_registry` table; provenance fields; enrichment jobs and dedupe utilities.
