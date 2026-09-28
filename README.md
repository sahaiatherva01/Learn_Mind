# School AI Platform (working title)

AI-powered academic platform: **teachers** create source-grounded, verified academic material; **students** practice, test and improve. Built on one **Question Intelligence Engine**.

- Boards/levels: ICSE 6–10 · ISC 11–12 · JEE · NEET · English only
- Subjects: Maths, Physics, Chemistry, Biology, Computer Science, History, Geography, English (phased)
- Roles: Admin → Incharges → Teachers (Subject/Class) → Students
- Tech: React + TypeScript · FastAPI · Supabase Postgres + pgvector · LangGraph/LangChain · Render
- Target: single school, ~3000 users, **ready by 1 Nov 2026**

## Docs
| File | Purpose |
|---|---|
| [PRD.md](PRD.md) | What, who, why, roles, features, permissions, workflows, scope |
| [ARCH.md](ARCH.md) | Layers, stack, agents, RAG, data model, security, deploy |
| [Rules.md](Rules.md) | Product, content, AI, security & engineering rules |
| [Phases.md](Phases.md) | Dated build plan, cut lines, risks |
| [Design.md](Design.md) | UX principles, tokens, components, screens |
| [Memory.md](Memory.md) | Decision log, open items, in-product memory design |

## Suggested repo layout
```
/backend   FastAPI app (api, core, db, services, jobs, llm, prompts)
/frontend  Vite + React + TS
/docs      these files
/prompts   versioned subject packs + eval sets
```

## Environment (backend)
```
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
JWT_SECRET=
LLM_PROVIDER_KEYS=
ALLOWED_ORIGINS=
```

## Quick start (once code exists)
```
cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload
cd frontend && npm i && npm run dev
```

## Status
Planning complete → start at **Phase 0** in `Phases.md`. Open items live in `Memory.md`.
# Learn_Mind
