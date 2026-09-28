# Memory.md — Project Memory

Two parts: (1) **project decision log** for humans/AI coding assistants, (2) **runtime memory design** for the product.

## Part 1 — Decision log (source of truth)

| # | Decision |
|---|---|
| 1 | Teacher uploads are **private to the uploading teacher** |
| 2 | Source label (book/page) shown to **teachers only**; students see question only |
| 3 | Search = **inside teacher-uploaded files only** (option a) |
| 4 | Boards: **ICSE 6–10 · ISC 11–12 · JEE · NEET** |
| 5 | All 8 subjects in V1, delivered in phases (PCM+CS first) |
| 6 | Class range same as #4 |
| 7 | English only |
| 8 | Diagrams phased: start with option a (extracted images + simple AI diagrams; RDKit for chem) |
| 9 | Students see correct answer only; teachers see method/steps; **solve twice + teacher approves** |
| 10 | Scanned PDFs: yes, but phased; import flow **asks teacher to confirm interpretation** |
| 11 | **Single school** first |
| 12 | Admin approves School → Incharges A/B/C approve Subject & Class Teachers → Class Teacher or Incharge approves student sections; all teachers can access students |
| 13 | Login: email, roll-no + school code, teacher-issued codes |
| 14 | DPDP / parental consent: **unanswered — OPEN** |
| 15 | Stack: HTML/CSS/JS + minimal React/TS, FastAPI, Supabase Postgres+pgvector, no Redis (Postgres job queue), LangGraph + LangChain (+CrewAI optional) |
| 16 | Free-tier models, no budget |
| 17 | ~3000 users, Render |
| 18 | Solo; full product by **1 Nov 2026** |
| 19 | Study Assistant **strictly grounded (RAG-only)** |
| 20 | Proctoring in V1 (students only) |
| 21 | Subjective answers: teacher manual grading; objective auto-graded |
| 22 | QIDs: long descriptive + short shareable |
| 23 | Bookmarks/favourites/collections; teacher folders/tags; student notes |
| 24 | Edits → **same QID + versions**, attempts pinned to version |
| 25 | "Unverified" badge until teacher approves |

## Open items / assumptions
- **DPDP compliance & parental consent** (students are minors) — decide before Phase 5.
- "All teachers have access to students" interpreted as **roster/basic lookup school-wide; analytics scoped to assigned sections/subjects**. Confirm.
- Render free tier has no background worker & sleeps → in-process worker at first.
- Chosen: **Vite+React+TS** rather than Next.js for V1 (revisit if SSR needed).
- CrewAI: off in V1 unless a concrete multi-agent need appears.
- Incharge A/B/C: assumed to be wing/section heads with equal approval power; confirm scopes.

## Glossary
QID = question ID · Long ID = descriptive · Short ID = `Q-XXXXXX` · Pack = config for a subject's generation · Preset = paper type layered on the engine · Unverified = AI content not yet teacher-approved.

## Part 2 — Runtime memory design (in-product)
| Memory | Scope | Contents | Used by |
|---|---|---|---|
| Teacher library memory | per teacher | files, chunks, chapter/topic tags | Studio, import |
| Question memory | school | questions, versions, verification runs | Bank, papers |
| Student learning profile | per student | topic accuracy, speed, difficulty history, weak topics, notes | Weak-topic engine, recommendations, assistant |
| Class memory | per section | aggregated weak topics, test history | Remedial planner |
| Session memory | per assistant chat | last N turns, current topic | Study Assistant |
| Preference memory | per teacher | default board/class/difficulty/style | Studio defaults |

Rules: memory contains no PII in LLM prompts; students can view their own profile; deletion supported; teacher library never shared across teachers.
