# Design.md — UX & UI Guidelines

## Principles
1. **Calm, academic, fast.** Minimal chrome; content first.
2. **Teacher = workspace, Student = focus.** Teacher UI is denser; student UI is clean and encouraging.
3. **Every question is a card with identity** (ID, status, origin).
4. **Never a dead end:** empty states say what to do next.
5. Accessible: WCAG AA contrast, keyboard navigable, 16px+ body, 44px touch targets.

## Tokens (plain CSS variables)
```
--bg:#F7F8FA  --surface:#FFFFFF  --ink:#1B1F2A  --muted:#6B7280  --line:#E5E7EB
--primary:#3B5BDB  --primary-ink:#FFFFFF
--ok:#2F9E44  --warn:#E8A317  --bad:#D6336C  --info:#1C7ED6
Font: Inter (UI), Source Serif 4 (question text), JetBrains Mono (code)
Radius: 10px · Spacing: 4/8/12/16/24/32 · Shadow: 0 1px 2px rgba(0,0,0,.06)
```
Light theme first; dark mode = Phase 5 stretch.

## Layout
Left nav (role-specific) + top bar (global **ID/question search**, notifications, profile). Max content width 1200px. Mobile: bottom tab bar for students.

## Key components
- **QuestionCard**: `[Short ID] · v2 · [Origin] · [Status]` header; body (KaTeX/code); meta chips (Class · Chapter · Topic · Difficulty · Marks); actions: ✓ select · ↻ regenerate · ✎ edit · ♡ favourite · 🔖 bookmark · ＋ collection · → add to paper. Teacher-only: **Source: Book, p.X**, "Show method".
- **Status badges:** `Unverified` (amber) · `Auto-checked ✓` (blue) · `Needs review ⚠` (red) · `Approved` (green).
- **ID chip:** shows short ID; click to copy; hover shows long ID (`MTH-12-INT-DEF-000482`).
- **Global search:** accepts long ID, short ID, `short@v2`, or text.
- **Progress bar rows** for subject/topic accuracy; **Weak topic pills** with priority colour.
- **Job toast/progress** for ingestion and generation.
- **Confirm-interpretation panel** (import): table of detected questions with editable chapter/type/difficulty, "Looks right" / "Fix".

## Screens
**Teacher:** Dashboard (My Classes) · Class view (Performance, Assignments, Tests, Question Bank, Worksheets, Quizzes, Mocks) · Library (upload, search, files) · **Question Studio** (stepper: Subject → Class → Chapter → Topic → Type → Difficulty → Count; mode toggle; results list) · Paper Builder (blueprint sections, swap, export) · Tests (schedule, results, proctoring log) · Analytics (topic heatmap, weak topics, Remedial Plan) · Collections.
**Student:** Dashboard (Upcoming · Practice · Progress · Weak areas) · Practice · Mock · Test (proctored) · Results & analysis · Study Assistant · Bookmarks/Notes.
**Admin/Incharge:** Approval queues · Schools · Teachers · Students · Sections · Subjects · Access.

## Question Studio wireframe
```
[Subject ▾] [Class ▾] [Chapter ▾] [Topic(s) ☑ multi]
[Mode: As-is | Similar | Higher]  [Type ▾]  [Difficulty: E M H]  [Count]
                     [ Generate ]
────────────────────────────────────────────
☑ Q-8K3F2A · v1 · AI_SIMILAR · Unverified      Source: RD Sharma p.212 (teacher only)
   ∫ ... dx ...                        [Show method] ♡ 🔖 ↻ ✎
────────────────────────────────────────────
[ Add selected → Worksheet ▾ ]
```

## Student test UI (proctored)
Full-screen, timer top-right, question palette left, autosave indicator. Pre-start notice listing monitored events. On violation: non-blocking banner "Tab switch detected (2)". No solutions shown mid-test.

## Results view
Score, accuracy, time vs allotted; strong/average/weak topics; correct answer only (no method); "Practice weak topics" CTA.

## Exports
PDF: clean serif, header (school, class, subject, marks, time), question IDs in small grey footer of each question (teacher key includes solution steps). Excel: sheets per report with frozen headers.

## Tone & copy
Encouraging for students ("Integration needs a little more practice"); precise for teachers. No jargon like "LLM" in UI; say "AI-generated · Unverified".
