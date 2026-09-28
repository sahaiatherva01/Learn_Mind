# ARCH — System Architecture

## 1. Layers

```
┌──────────────────────────────────────────────┐
│ FRONTEND   Vite + React + TypeScript (SPA)    │  Render Static Site
│            plain CSS design tokens, KaTeX      │
└───────────────────────┬──────────────────────┘
                        ▼  HTTPS / JSON (JWT)
┌──────────────────────────────────────────────┐
│ API / BACKEND   FastAPI (Python)              │  Render Web Service
│  auth · RBAC · REST routers · validation       │
└───────────────────────┬──────────────────────┘
                        ▼
┌──────────────────────────────────────────────┐
│ BUSINESS LOGIC                                │
│  Question Engine · Verification · Blueprints   │
│  Analytics · Weak-Topic Engine · Proctoring    │
│  Agents (LangGraph) · RAG (LangChain)          │
└───────────────────────┬──────────────────────┘
                        ▼
┌──────────────────────────────────────────────┐
│ DATABASE   Supabase Postgres + pgvector       │
│  relational + vectors + job queue + RLS        │
│  Supabase Storage (PDFs, exports)              │
└───────────────────────┬──────────────────────┘
                        ▼
┌──────────────────────────────────────────────┐
│ EXTERNAL   LLM (free tiers) · Embeddings ·    │
│  Supabase Auth/Storage · RDKit (local) ·       │
│  PDF/Excel libs (local)                        │
└──────────────────────────────────────────────┘
```

## 2. Stack decisions (and why)

| Area | Choice | Reason |
|---|---|---|
| Frontend | **Vite + React + TS**, plain CSS tokens | Fastest for solo; static hosting is free on Render; Next.js SSR adds deploy weight with no V1 benefit |
| Math/Chem render | KaTeX, RDKit (server) → SVG | LaTeX + SMILES structures |
| Backend | **FastAPI** + Pydantic v2 + SQLAlchemy/asyncpg | Async, typed, LangGraph-friendly |
| DB | **Supabase Postgres + pgvector** | Render's free Postgres expires; Supabase free persists |
| Auth | Supabase Auth (email) + custom roll-no/school-code and teacher-issued codes → same JWT | "Allow everything" login |
| Queue | **Postgres job table** (`FOR UPDATE SKIP LOCKED`) + one worker process | No Redis needed at this scale; swap to Redis/RQ later behind `JobQueue` interface |
| Agents | **LangGraph** (orchestration), **LangChain** (loaders, splitters, retrievers), **CrewAI** = optional, off by default in V1 | One orchestration framework keeps a solo build debuggable |
| LLM | Free tiers, **tiered**: small/fast for tagging & routing; stronger free model for generation & verification. Provider behind `LLMClient` interface | No budget; rate limits are the main constraint |
| Hosting | **Render**: static site + web service + background worker | Requested |

## 3. Backend modules

```
app/
  api/            routers: auth, admin, teacher, student, library, questions,
                  studio, papers, tests, analytics, exports, assistant
  core/           config, security (JWT, RBAC), logging, errors
  db/             models, migrations (Alembic), RLS SQL
  services/
    ingestion/    pdf parse, chunk, embed, chapter/topic tagging
    retrieval/    hybrid search (pgvector + full-text), per-teacher scoping
    questions/    ids, versions, metadata, bank, bookmarks
    generation/   subject packs, prompt builders, LangGraph graphs
    verification/ solve-twice, agreement check, status machine
    papers/       blueprints, presets, assemblers
    tests/        scheduling, attempts, grading, proctoring events
    analytics/    topic stats, weak-topic engine, remedial planner
    exports/      PDF (WeasyPrint/ReportLab), Excel (openpyxl)
    assistant/    grounded study assistant
  jobs/           queue, worker, handlers
  llm/            LLMClient, rate limiter, cache, model tiers
```

## 4. Agentic AI design (LangGraph graphs)

**G1 Ingestion graph:** `parse → clean → chunk → embed → detect chapters/topics → detect question blocks → store → notify`
**G2 Question-set interpretation graph:** `extract questions → classify (type/chapter/difficulty/marks) → build interpretation summary → WAIT for teacher confirm → import`
**G3 Generation graph:** `plan (params → blueprint) → retrieve source chunks → draft → self-critique (syllabus, style, difficulty) → solve #1 → solve #2 (independent prompt/model) → compare → status`
 - agree → `UNVERIFIED (auto-checked ✓)` ; disagree → flagged `NEEDS_REVIEW` (teacher sees both solutions)
 - Objective answers: auto key. Subjective: solution steps for teacher; rubric draft; manual grading.
**G4 Paper assembly graph:** `blueprint → pick from bank → generate gaps → dedupe → balance difficulty/topics → render`
**G5 Weak-topic graph (mostly deterministic, LLM only for explanation):** `attempts → topic mapping → accuracy+time+difficulty → priority → recommendations`
**G6 Remedial planner:** `class weak topics → 5-day plan (revise → basic → medium → hard → mini-test) → teacher review → assign`
**G7 Study assistant:** `query → retrieve ONLY teacher-assigned material + syllabus → grounded answer w/ citations → Explain/Example/Try/Practice/Check flow; if no evidence → say so`

## 5. RAG design
- Chunking: structure-aware (headings, question blocks, page anchors); chunk metadata = `{teacher_id, file_id, page, chapter, topic, kind: theory|question|solution}`.
- Store: `chunks(embedding vector(768/1024), tsv tsvector)`; hybrid retrieval (vector + BM25-ish FTS) → rerank (light).
- **Isolation:** every retrieval filtered by `teacher_id` (library private) via query + Postgres RLS. Study assistant retrieves from *assignment-scoped* material only.
- Syllabus store: seeded ICSE/ISC/JEE/NEET chapter–topic trees (`syllabus_nodes`) used for tagging & constraint.
- Provenance: `source_label` (book, page) stored on the question, **returned only to teacher roles**.

## 6. Data model (core tables)

```
schools, users, roles/memberships, incharges, teacher_assignments(teacher, section, subject)
sections, subjects, student_enrollments(status: pending|approved)
files, chunks, syllabus_nodes(board, class, subject, chapter, topic)
questions(qid, short_id, long_id, origin, source_ref, owner_teacher_id, current_version)
question_versions(qid, version, body, options, answer, solution, meta, verification_status, created_by)
verification_runs(qid, version, run_no, solver_model, answer, steps, agree)
collections, collection_items, bookmarks, favourites, question_notes
papers, paper_items(qid, version, marks), assignments
tests(schedule, duration, proctor_cfg), attempts, attempt_answers(qid, version, ...), proctor_events
topic_stats, weak_topics, remedial_plans
jobs(type, payload, status, attempts, run_at, locked_by), audit_log, llm_cache
```
- `attempt_answers` references **(qid, version)** → attempts pinned to version.
- Verification states: `DRAFT → UNVERIFIED(auto ✓ | ⚠ disagree) → APPROVED | REJECTED`.

## 7. Security & privacy
- JWT + RBAC dependency on every route; Postgres **RLS** as second wall.
- Private libraries: strict owner scoping; no cross-teacher retrieval; signed URLs for files.
- Students never receive `solution`, `source_ref`, or other teachers' data (server-side field filtering, not UI hiding).
- Minors' data: minimal fields, no third-party trackers, LLM prompts contain no student PII, audit log, deletion path. **DPDP requirements: open item (see Memory.md).**
- Proctoring events stored per attempt; teachers review, no auto-punish.
- Rate limiting + per-user LLM quotas.

## 8. Free-tier LLM strategy (no budget, 3000 users)
- Students **don't** trigger heavy generation; practice is served from the approved bank → LLM load ≈ teachers + study assistant.
- Aggressive **caching** (`llm_cache` by prompt hash), batch generation, background queue with backoff, provider fallback chain.
- Solve-twice doubles cost → run only on generation/import, not on reads; objective questions get cheaper checks first (numeric/SymPy check, RDKit for chem) before second LLM pass.
- Study assistant: small model, short context, per-student daily cap.

## 9. Deployment (Render)
- `web` (FastAPI) · `worker` (job runner) · `static` (frontend) · Supabase (DB/Storage/Auth).
- Free web services sleep → use a paid-lite tier at launch for the demo, or a keep-alive ping; workers on free tier are **not available** (Render free has no background workers) → V1 fallback: run worker loop inside web service as a background task, split later.
- Env: `DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_KEY, JWT_SECRET, LLM_PROVIDER_KEYS, ALLOWED_ORIGINS`.
- Capacity: 3000 total users, ≈300–600 concurrent peak during scheduled tests → attempts autosave every N seconds, answers batched.

## 10. Observability
Structured logs, job dashboard (admin), LLM call log (latency, tokens, cache hit), error tracking (Sentry free).
