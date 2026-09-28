# Rules.md — Product, Content, Engineering & AI Rules

## A. Product rules
1. **Scope lock:** no operations features (attendance, fees, timetable, parent portal, HR, transport). Reject scope creep; log in `Phases.md` backlog.
2. **One engine:** worksheets/quizzes/papers/mocks/pre-boards are presets over the Question Engine. Never build a separate generator.
3. **Privacy by default:** a teacher's uploads are visible **only to that teacher**. No sharing in V1.
4. **Source label** (book/page) appears **only in teacher/incharge UI**. Never in student API responses.
5. Students see **the correct answer only**; teachers/incharges see **method, steps, verification history**.
6. Teachers act only on **assigned sections & subjects**.
7. Student→section approval: **Class Teacher or Incharge only**.
8. English-only V1.

## B. Question & ID rules
1. Every question — AI-generated, copied from source, imported or teacher-authored — has a **long ID and short ID** at creation.
2. IDs are **immutable**. Edits create a new **version** under the same QID; never fork silently.
3. Attempts, papers and assignments reference **(QID, version)**.
4. Required metadata: subject, class, board/exam, chapter, topic, type, difficulty, marks, origin, verification status.
5. Origin enum: `SOURCE_COPY | AI_SIMILAR | AI_HIGHER | TEACHER_AUTHORED`.
6. Search must resolve long ID, short ID, or `short@vN`.
7. Duplicate detection (embedding + text hash) before saving to bank.

## C. Correctness rules (make-or-break)
1. **Solve-twice:** two independent solves; answers compared (numeric tolerance / symbolic / string normalization).
2. Status starts **Unverified** for all AI content; only a teacher's explicit approval → `Approved`.
3. Disagreement → `Needs Review` with both solutions shown to teacher; never auto-publish.
4. Objective (MCQ, numerical, assertion-reason, output-based): auto-graded. Subjective: teacher manual grading.
5. Students can only be assigned **Approved** questions (unless the teacher explicitly overrides with a visible warning).
6. Prefer tool checks over LLM opinion: SymPy for math, code execution sandbox for CS output questions, RDKit for chemistry structures/SMILES.
7. Never invent source citations. If unsure, omit.
8. **Interpretation confirmation:** uploaded question sets require a teacher confirmation step before import.

## D. AI / RAG rules
1. Teacher generation is grounded in that teacher's library + syllabus tree; if retrieval is weak, say so and label output "not source-grounded".
2. **Study Assistant is strictly grounded** (teacher-assigned material + syllabus). No general-knowledge fallback in V1. Out-of-scope → polite refusal + suggest asking teacher.
3. Class-level appropriate language; no jumping beyond syllabus for ICSE/ISC; JEE/NEET style only when flagged.
4. Prompts are versioned files (`/prompts/<subject>/<type>.md`) with eval sets; no inline prompt strings scattered in code.
5. LLM calls go through `LLMClient` (retry, rate limit, cache, logging). No direct SDK calls elsewhere.
6. No student PII in prompts.
7. Reproduce source questions **as-is only for the owning teacher**; students never see source text as "book content"; only the question.
8. Copyright: upload requires disclaimer acceptance ("I have the right to use this material for teaching"). Files private; no public distribution.

## E. Security rules
1. Every route has an explicit role dependency; default deny.
2. RLS enabled on all tenant tables; service key only on backend.
3. Field-level filtering server-side for student responses.
4. Secrets only via env; never commit `.env`.
5. Rate-limit auth, upload, generation endpoints.
6. Upload validation: type (PDF), size cap, malware-safe parsing, no execution.
7. Minors: collect minimum data; log access; support deletion/export.

## F. Proctoring rules (students only)
1. Detect tab switch, window blur, fullscreen exit, copy/paste attempts, repeated reloads.
2. Log events; show counts to teacher; **warn** student; no automatic disqualification.
3. Teachers are not proctored.
4. Be transparent: students told what is monitored before start.

## G. Engineering rules
1. Python 3.11+, type hints, Ruff + Black; TypeScript strict on frontend.
2. Alembic migrations only; no manual DB edits.
3. Tests: unit for ID/versioning, permissions, grading, verification comparison; integration for generation graph (mock LLM).
4. Small PRs/commits daily; `main` always deployable.
5. Feature flags for unfinished subject packs.
6. Config-driven subject packs (YAML/JSON) instead of hard-coded subject logic.
7. Async everywhere for I/O; long tasks → job queue, never in request cycle.
8. Errors: typed exceptions → consistent JSON error shape.
9. Logs: no PII, no full prompts in production logs.

## H. UX rules
1. Student UI stays uncluttered: dashboard → practice → results.
2. Any AI output is editable before saving.
3. Every generated question shows ID + status badge.
4. Never block teacher on a slow job; show progress and allow leaving the page.
