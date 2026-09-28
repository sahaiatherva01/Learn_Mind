# Question Studio API router per Rules.md C.1-C.8, G.6, ARCH.md §4
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_teacher
from app.db.models import User
from app.db.session import get_db
from app.schemas.studio import (
    ConfirmImportSetRequest,
    InterpretSetRequest,
    InterpretSetResponse,
    SaveDraftRequest,
    StudioGenerateRequest,
    StudioGenerateResponse,
)
from app.services.generation.studio import question_studio_service
from app.services.generation.subject_packs import subject_pack_manager
from app.services.ingestion.set_importer import question_set_importer

router = APIRouter()


@router.get("/subject-packs")
async def list_subject_packs(
    current_user: User = Depends(require_teacher),
) -> list[dict[str, Any]]:
    """
    Returns available subject packs with chapters, topics, and question types.
    """
    return subject_pack_manager.list_packs()


@router.post("/generate", response_model=StudioGenerateResponse)
async def generate_question_draft(
    payload: StudioGenerateRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    G3 Question Studio Generation Pipeline:
    Drafts question + executes independent Solve-Twice Verification + Tool checks.
    """
    draft_result = await question_studio_service.generate_draft_question(
        db=db,
        teacher_id=current_user.id,
        subject=payload.subject,
        class_level=payload.class_level,
        chapter=payload.chapter,
        topic=payload.topic,
        question_type=payload.question_type,
        difficulty=payload.difficulty,
        marks=payload.marks,
        mode=payload.mode,
        chunk_id=payload.chunk_id,
        mixed_topics=payload.mixed_topics,
    )
    return draft_result


@router.post("/save-draft", status_code=status.HTTP_201_CREATED)
async def save_draft_question(
    payload: SaveDraftRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Saves a verified or reviewed draft question into the Question Bank.
    If approve=True, marks verification_status='APPROVED'.
    """
    result = await question_studio_service.save_draft_to_bank(
        db=db,
        teacher_id=current_user.id,
        school_id=current_user.school_id,
        draft_payload=payload.model_dump(),
        approve=payload.approve,
    )
    await db.commit()
    return result


@router.post("/interpret-set", response_model=InterpretSetResponse)
async def interpret_question_set(
    payload: InterpretSetRequest,
    current_user: User = Depends(require_teacher),
) -> dict[str, Any]:
    """
    G2 Question-set import (Step 1):
    Parses raw unformatted questions and builds an Interpretation Summary for teacher confirmation.
    Rules.md C.8: Uploaded question sets require a teacher confirmation step before import.
    """
    result = await question_set_importer.parse_and_interpret_set(
        raw_text=payload.raw_text,
        board=payload.board,
        class_level=payload.class_level,
        subject=payload.subject,
    )
    return result


@router.post("/confirm-import-set", status_code=status.HTTP_201_CREATED)
async def confirm_and_import_question_set(
    payload: ConfirmImportSetRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    G2 Question-set import (Step 2):
    Teacher confirms the interpretation -> Batch imports questions with Solve-Twice verification.
    """
    imported = await question_set_importer.confirm_and_import_set(
        db=db,
        teacher_id=current_user.id,
        school_id=current_user.school_id,
        confirmed_questions=payload.questions,
        source_ref=payload.source_ref,
    )
    await db.commit()
    return {
        "imported_count": len(imported),
        "questions": imported,
        "message": f"Successfully imported {len(imported)} questions with Solve-Twice verification",
    }
