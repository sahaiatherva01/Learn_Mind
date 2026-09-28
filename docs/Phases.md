# Phases.md — Build Plan (28 Sep → 1 Nov 2026)

**Reality check:** ~34 days, solo, whole product, free-tier LLMs. Achievable only if (a) subjects are **config-driven packs** on one engine, (b) V1 is *good, not gold-plated*, and (c) risky items have cut lines. Order below is by dependency and risk — the demo-critical path comes first.

## Phase 0 — Foundations (28 Sep – 1 Oct, 4 days)
- Repo, Render + Supabase setup, CI, env, Alembic, base FastAPI, React shell
- Auth (email + roll-no/school-code + teacher-issued codes), JWT, RBAC, RLS
- Admin → School approval → Incharge → Teacher/Student approval flows
- Sections, subjects, teacher assignments
- **Exit:** all three roles can log in and see role-correct empty dashboards.

## Phase 1 — Library + RAG (2 – 8 Oct, 7 days)
- Private PDF upload, disclaimer, storage, job queue + worker
- Parse → chunk → embed → tag chapter/topic (syllabus seeds: ICSE/ISC/JEE/NEET PCM+CS first)
- Search inside own files (option a), source label (teacher-only)
- **Exit:** teacher uploads a book, searches it, sees ready status.
- **Cut line:** OCR/scanned PDFs → out (V1.1).

## Phase 2 — Question Engine + Studio (9 – 17 Oct, 9 days) ⭐ core
- Question ID system (long + short), versions, metadata, bookmarks/favourites/collections/notes, ID search
- Question Studio: modes As-is / Similar / Higher / Mixed topics; select/regenerate/edit/save
- **Solve-twice verifier**, Unverified badge, approval, teacher solution view / student answer-only
- Question-set import with **interpretation confirmation**
- Subject packs at full depth: **Mathematics, Physics, Chemistry (incl. reaction chains + RDKit), Computer Science**
- **Exit:** approved questions with IDs saved in a bank.
- **Cut line:** complex AI diagrams → extracted images + simple SVG only.

## Phase 3 — Papers, Tests, Proctoring, Analytics (18 – 26 Oct, 9 days)
- Presets: Worksheet, Quiz (Speed Mode), Question Paper, Class Test, Mock, Pre-Board; mixed topics; swap questions
- PDF export (student + teacher key); Excel export
- Test scheduling; student attempt UI; **proctoring (tab switch etc.)**; auto-grade objective; manual grade subjective
- Weak-topic engine; student progress; class analytics; **Remedial Plan**
- Student dashboard, practice assignments, mocks
- **Exit:** full end-to-end demo loop works.

## Phase 4 — Remaining subjects + Study Assistant (27 – 30 Oct, 4 days)
- Packs: **Biology (NEET), History, Geography, English** on the same engine (prompts + blueprints + eval sets)
- Grounded Study Assistant (RAG-only, Explain→Example→Try→Practice→Check)
- **Cut line:** Bio diagram-labelling limited to extracted images; Geography map-based limited to text-based/simple.

## Phase 5 — Hardening (31 Oct – 1 Nov, 2 days)
- Load sanity (test-day concurrency), permission audit, bug bash, seed demo data, docs, deploy freeze
- Privacy pass (student data, consent flow, DPDP items — once specified)

## Risk register
| Risk | Impact | Mitigation |
|---|---|---|
| Free-tier LLM rate limits | Generation stalls | Queue + cache + fallback providers; students use approved bank |
| Solve-twice doubles usage | Quota burn | Tool checks first (SymPy/RDKit); second LLM pass only when needed |
| 8 subjects in 5 weeks | Quality dip | Config packs; PCM+CS depth first; others baseline |
| Render free tier sleeps / no free worker | Demo latency | In-process worker at first; paid-lite tier for demo |
| Scope creep | Miss date | Rules.md scope lock; backlog below |
| Solo dependency | Single failure point | Daily commits, deployable main |
| DPDP/minors compliance undefined | Launch blocker | Decide before Phase 5 |

## Definition of Done (1 Nov)
Upload → Generate → Verify/Approve → Assemble → Export → Schedule → Proctored attempt → Analytics → Remedial plan — all working for PCM+CS, with baseline coverage for the other four subjects.

## Backlog (post-V1)
OCR · school-shared library · multi-school · SSO · handwritten grading · Hindi · global curated library · parent view · adaptive tests · mobile app.
