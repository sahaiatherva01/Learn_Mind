# Pydantic schemas for Question Bank, Versioning & Collections
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VerificationRunSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_no: int
    solver_model: str
    answer: str
    steps: str | None = None
    agree: bool
    diff_notes: str | None = None


class QuestionVersionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version: int
    body: str
    options: list[str] | None = None
    answer: str
    solution: str | None = None  # None for students per Rules.md A.5
    verification_status: str
    meta: dict[str, Any] | None = None
    verification_runs: list[VerificationRunSchema] = []


class QuestionDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    short_id: str
    long_id: str
    origin: str
    source_ref: str | None = None  # None for students per Rules.md A.4
    owner_teacher_id: str
    current_version: int
    version_data: QuestionVersionSchema
    created_at: str


class CreateQuestionRequest(BaseModel):
    subject: str
    class_level: int
    chapter: str
    topic: str
    origin: str = "TEACHER_AUTHORED"  # SOURCE_COPY | AI_SIMILAR | AI_HIGHER | TEACHER_AUTHORED
    body: str
    options: list[str] | None = None
    answer: str
    solution: str | None = None
    marks: int = 1
    difficulty: str = "MEDIUM"
    question_type: str = "MCQ"
    source_ref: str | None = None
    verification_status: str = "UNVERIFIED"
    meta: dict[str, Any] | None = None


class EditQuestionRequest(BaseModel):
    body: str
    options: list[str] | None = None
    answer: str
    solution: str | None = None
    verification_status: str = "UNVERIFIED"
    meta: dict[str, Any] | None = None


class QuestionStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(APPROVED|REJECTED|NEEDS_REVIEW|UNVERIFIED)$")


# Organization schemas: Bookmarks, Favourites, Notes, Collections
class BookmarkRequest(BaseModel):
    qid: str


class FavouriteRequest(BaseModel):
    qid: str


class QuestionNoteRequest(BaseModel):
    qid: str
    note_text: str


class CollectionCreateRequest(BaseModel):
    name: str
    description: str | None = None


class AddToCollectionRequest(BaseModel):
    collection_id: str
    qid: str
    version: int = 1
