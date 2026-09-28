# PRD — School AI Platform (working title)

> **One line:** An AI-powered academic platform where teachers create high-quality, source-grounded academic material and students practice intelligently.
> Narrow V1, deep academic intelligence. **No school ERP.**

---

## 1. What are we building?

A single-school web platform (multi-school later) with three roles — **Teacher, Student, Admin/Incharge hierarchy** — built around **one Question Intelligence Engine**.

```
                    QUESTION INTELLIGENCE ENGINE
                              │
     ┌────────────┬───────────┼───────────┬────────────┐
 Worksheet      Quiz        Paper       Mock       Pre-Board
```

Everything (worksheets, quizzes, papers, mocks, pre-boards, practice, remedial plans) is a *view/preset* on top of the same engine, the same question bank and the same metadata.

**Core capabilities**
- Teacher uploads books / PDFs / question sets → private, searchable knowledge base (RAG).
- **Question Studio**: generate questions *as-is from source*, *similar*, or *slightly higher level*, with subject-specific logic.
- Every question has a **Question ID** (long + short), version history, bookmarks, favourites, collections.
- **Solve-twice verification** + "Unverified" badge until a teacher approves.
- Assessment: tests, scheduling, proctoring (students), performance, weak topics, remedial plans.
- Student: dashboard, grounded AI Study Assistant, practice, mocks, progress, weak-topic engine.
- Export: PDF and Excel.

## 2. Who uses it?

| Role | Who | Primary job |
|---|---|---|
| **Admin** | You (platform owner) | Approve school, manage platform |
| **Incharge (A/B/C)** | Senior school staff (e.g. wing/section heads) | Approve Subject/Class Teachers, approve student sections |
| **Class Teacher** | Teacher owning a section | Approve student → section, class analytics |
| **Subject Teacher** | Teacher for a subject in assigned sections | Create content, assess, remediate |
| **Student** | Class 6–12, JEE/NEET aspirants | Practice, test, improve |

Boards/levels: **ICSE (6–10) · ISC (11–12) · JEE · NEET**. Language: **English only**.

## 3. What problem does it solve?

- Teachers spend hours making worksheets/papers from books; generic AI gives wrong, off-syllabus, non-board-style questions.
- No trust in AI answer keys → teachers re-solve everything.
- No question-level traceability (where did this come from? was it used before?).
- Students get generic practice, not targeted to weak topics.
- Class-level weak topics are not turned into action (remedial plans).

## 4. User roles & hierarchy

```
Admin (you)
  └─ approves ─► School
        └─ School Incharges A, B, C
              ├─ approve ─► Subject Teachers
              ├─ approve ─► Class Teachers
              └─ approve ─► Student → Section assignment (also Class Teacher)
```
- All teachers can **access students** (roster/lookup). Section assignment approval: **Class Teacher or Incharge only**.
- Teacher's class-level analytics/content actions are limited to **assigned sections + subjects** (see Permissions).

## 5. Features

### 5.1 Teacher
1. **Class management** — assigned sections, subject access, chapter/topic selection.
2. **Library** — upload PDFs (private), search inside own files (option a), source label (book, page) visible to teacher only. Scanned PDFs/OCR: phased.
3. **Question Studio** — Subject → Class → Chapter → Topic → Type → Difficulty → Count; modes: *From source (as-is)*, *Similar*, *Higher level*, *Mixed topics*. Select / Regenerate / Edit / Save / Add to Paper.
4. **Upload question sets** — AI analyzes set, shows *"Here is how I interpreted this (chapters, types, difficulty, marks)"* → teacher confirms/corrects before import.
5. **Question IDs & metadata** — see §5.5.
6. **Verification** — solve-twice; "Unverified" until teacher approves; teacher sees method + steps.
7. **Generators (presets)** — Worksheet (student version + teacher key), Quiz (incl. Speed Mode), Question Paper, Class Test, Mock, Pre-Board.
8. **Assessment** — schedule tests, results, topic-wise performance, weak-topic identification, **Remedial Plan**.
9. **Export** — PDF (worksheet, quiz, paper, key, remedial) and Excel (scores, topics, analytics, question bank).

### 5.2 Student
Dashboard (upcoming, practice, progress, weak areas) · **AI Study Assistant (strictly grounded / RAG-only)** · Practice assignments · Practice questions · Mock tests · Progress tracking · Weak-topic detection · Recommended practice · Proctored scheduled tests.
Students see **only the correct answer** (no method) after submission, per teacher settings.

### 5.3 Admin / Incharge
Schools · Teachers · Students · Classes/Sections · Subjects · Access control · Approval queues.

### 5.4 Subject Intelligence (generation packs)
| Subject | Question families |
|---|---|
| Mathematics | Board (E/M/H), JEE Main/Advanced style, step-by-step long answers |
| Physics | Theory, numericals, conceptual, HOTS, derivations, assertion-reason, JEE/NEET |
| Chemistry | Theory, reasoning, equations, **reaction chains (A→B→C→D)**, mechanisms, conversions, JEE/NEET |
| Biology | Theory, diagrams, labelling, reasoning, case-based, assertion-reason, NCERT-based, NEET |
| Computer Science | Theory, programming, debugging, output-based, code completion, SQL, case-based |
| History / Geography | Board, short/long, source/case-based, map-based (Geo), HOTS |
| English | Literature, reading comprehension, analytical, short/long, case-based |

### 5.5 Question ID system
- **Long ID** (descriptive): `MTH-12-INT-DEF-000482` → `SUBJECT-CLASS-CHAPTER-TOPIC-SEQ`.
- **Short ID** (share/search): `Q-8K3F2A` (base32, no ambiguous chars).
- Both resolve to the same question. Search box accepts either.
- **Versioning**: edits create `v2`, `v3` under the **same QID**; attempts pinned to the version taken. Displayed as `Q-8K3F2A · v2`.
- Metadata per question: subject, class, board/exam (ICSE/ISC/JEE/NEET), chapter, topic, type, difficulty, marks, origin (`SOURCE_COPY` | `AI_SIMILAR` | `AI_HIGHER` | `TEACHER_AUTHORED`), source label (teacher-only), verification status, version, creator, timestamps.
- Actions: bookmark, favourite, add to collection/folder/tag (teacher), student notes on question.

## 6. Permissions

| Capability | Admin | Incharge | Class Teacher | Subject Teacher | Student |
|---|:-:|:-:|:-:|:-:|:-:|
| Approve school | ✓ | – | – | – | – |
| Approve teachers | – | ✓ | – | – | – |
| Approve student → section | – | ✓ | ✓ | – | – |
| View student roster/profile (basic) | ✓ | ✓ | ✓ | ✓ | – |
| View section analytics | ✓ | ✓ | own section | assigned sections/subjects | own only |
| Upload/see own library | – | – | own | own | – |
| See any other teacher's library | ✗ | ✗ | ✗ | ✗ | ✗ |
| Question Studio | – | ✓ | ✓ | ✓ | – |
| Approve/verify a question | – | ✓ | ✓ | ✓ (own subject) | – |
| See source label / solution steps | – | ✓ | ✓ | ✓ | ✗ (answer only) |
| Schedule tests | – | ✓ | ✓ | ✓ | – |
| Take tests / practice | – | – | – | – | ✓ (proctored) |
| Bookmark / favourite | – | ✓ | ✓ | ✓ | ✓ |

> **Assumption to confirm:** "all teachers have access to students" = roster/basic profile lookup school-wide; *performance analytics* stay limited to assigned sections/subjects.

## 7. User workflows

**W1 Onboarding:** Admin creates/approves School → Incharges added → teachers register (email) → Incharge approves as Subject/Class Teacher → students join via email / roll-no + school code / teacher-issued code → Class Teacher/Incharge approves section.

**W2 Ingest:** Teacher uploads PDF → job queue → parse/chunk/embed → tag chapters/topics → "Ready" (private).

**W3 Generate:** Question Studio → choose mode & parameters → agent retrieves source chunks → drafts → **solve-twice verify** → shows as *Unverified* → teacher edits/approves → saved to bank with IDs.

**W4 Import question set:** Upload → AI interpretation summary → teacher confirms/corrects → questions imported with IDs (`SOURCE_COPY`).

**W5 Build paper:** Preset (Worksheet/Quiz/Paper/Mock/Pre-Board) → auto blueprint → auto-fill from bank/generate → swap questions → export PDFs (student + key).

**W6 Schedule test:** Choose class/date/time/duration → students see it → proctored attempt → auto-grade objective, teacher manual-grades subjective → analytics.

**W7 Improve:** Attempts → weak-topic engine → student recommended practice; class weak topics → teacher generates **Remedial Plan** → assign.

**W8 Study Assistant:** Student asks → retrieve from teacher-assigned material + syllabus only → Explain → Example → Try yourself → Practice → Check.

## 8. What is NOT included
Attendance · Fees · Timetable · Parent portal · HR/Payroll · Transport · Library lending · Multi-school SaaS (V1) · Hindi/regional languages · Handwritten-answer AI grading · Global public question library (NCERT/PYQ) · Mobile apps · Live classes · Complex organic-structure image generation beyond SMILES/RDKit · Payments.

## 9. MVP scope (must ship by 1 Nov)
Everything in §5 for a **single school**, with subjects delivered by **config-driven generation packs**. See `Phases.md` for cut lines: PCM + CS at full depth first; Biology / History / Geography / English packs at "good baseline" depth.

Definition of Done for V1: a real teacher can upload a PDF, generate + approve questions with IDs, export a worksheet/paper (PDF), schedule a proctored test; students take it; teacher sees weak topics and a remedial plan.

## 10. Future versions
- V1.1 OCR for scanned books · school-shared library toggle (with copyright controls) · diagram generation upgrades
- V2 Multi-school tenancy · SSO (Google/Microsoft) · AI-assisted handwritten answer grading · Hindi medium · seeded NCERT/public-domain library
- V3 Parent view (read-only) · adaptive testing · mobile app · analytics benchmarking across sections
