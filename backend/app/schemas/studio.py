# Pydantic schemas for Question Studio & Question Set Importer
from typing import Any

from pydantic import BaseModel, Field


class StudioGenerateRequest(BaseModel):
    subject: str
    class_level: int = Field(..., ge=6, le=12)
    chapter: str
    topic: str
    question_type: str = "MCQ"  # MCQ, NUMERICAL, STEP_BY_STEP, PROOF, CODE_OUTPUT, REACTION_CHAIN
    difficulty: str = "MEDIUM"  # EASY, MEDIUM, HARD
    marks: int = 1
    mode: str = "AI_SIMILAR"  # SOURCE_COPY, AI_SIMILAR, AI_HIGHER, MIXED_TOPICS
    chunk_id: str | None = None
    mixed_topics: str | None = None


class DraftQuestionData(BaseModel):
    body: str
    options: list[str] | None = None
    answer: str
    solution: str | None = None


class SolverDetail(BaseModel):
    model: str
    answer: str
    steps: str
    tool_meta: dict[str, Any] | None = None


class VerificationDetail(BaseModel):
    agree: bool
    status: str
    diff_notes: str | None = None
    solver1: SolverDetail
    solver2: SolverDetail


class StudioGenerateResponse(BaseModel):
    subject: str
    class_level: int
    chapter: str
    topic: str
    question_type: str
    difficulty: str
    marks: int
    mode: str
    source_ref: str | None = None
    draft: DraftQuestionData
    verification: VerificationDetail


class SaveDraftRequest(BaseModel):
    subject: str
    class_level: int
    chapter: str
    topic: str
    question_type: str = "MCQ"
    difficulty: str = "MEDIUM"
    marks: int = 1
    mode: str = "AI_SIMILAR"
    source_ref: str | None = None
    draft: DraftQuestionData
    verification: VerificationDetail
    approve: bool = False


# Question Set Importer Schemas
class InterpretSetRequest(BaseModel):
    raw_text: str
    board: str = "ICSE"
    class_level: int = 12
    subject: str = "Mathematics"


class InterpretSetResponse(BaseModel):
    interpretation_summary: str
    detected_subject: str
    detected_class: int
    questions_count: int
    questions: list[dict[str, Any]]


class ConfirmImportSetRequest(BaseModel):
    questions: list[dict[str, Any]]
    source_ref: str | None = "Imported Question Set"
