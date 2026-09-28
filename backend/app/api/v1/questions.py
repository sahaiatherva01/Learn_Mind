# Question Bank API router per Rules.md A.4, A.5, B.1-B.7, E.1
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import (
    get_current_active_user,
    require_teacher,
)
from app.db.models import (
    Bookmark,
    Collection,
    CollectionItem,
    Favourite,
    Question,
    QuestionNote,
    QuestionVersion,
    User,
)
from app.db.session import get_db
from app.schemas.question import (
    AddToCollectionRequest,
    BookmarkRequest,
    CollectionCreateRequest,
    CreateQuestionRequest,
    EditQuestionRequest,
    FavouriteRequest,
    QuestionNoteRequest,
    QuestionStatusUpdateRequest,
)
from app.services.questions.bank import question_bank_service

router = APIRouter()


@router.get("/search")
async def search_questions(
    q: str | None = Query(None, description="Short ID (Q-8K3F2A), Long ID, short@vN, or text"),
    subject: str | None = None,
    class_level: int | None = None,
    chapter: str | None = None,
    status: str | None = None,
    origin: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Search question bank. Resolves Short IDs, Long IDs, version queries (short@v2), and text.
    Enforces student field-level redaction per Rules.md A.4 & A.5.
    """
    # If student, force status to APPROVED only per Rules.md C.5
    search_status = "APPROVED" if current_user.role == "STUDENT" else status

    results = await question_bank_service.search_questions(
        db=db,
        school_id=current_user.school_id,
        raw_query=q,
        subject=subject,
        class_level=class_level,
        chapter=chapter,
        status=search_status,
        origin=origin,
        limit=limit,
        offset=offset,
    )

    if current_user.role == "STUDENT":
        results = [question_bank_service.sanitize_for_student(item) for item in results]

    return {"total": len(results), "questions": results}


@router.get("/{qid}")
async def get_question_detail(
    qid: str,
    v: int | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get question by QID or Short ID, with full version history and verification runs.
    """
    stmt = (
        select(Question)
        .options(
            selectinload(Question.versions).selectinload(QuestionVersion.verification_runs)
        )
        .where(
            and_(
                Question.school_id == current_user.school_id,
                (Question.id == qid) | (Question.short_id == qid.upper()) | (Question.long_id == qid.upper()),
            )
        )
    )
    result = await db.execute(stmt)
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    # Select target version
    target_v = None
    if v:
        for item in question.versions:
            if item.version == v:
                target_v = item
                break
    if not target_v:
        for item in question.versions:
            if item.version == question.current_version:
                target_v = item
                break
    if not target_v and question.versions:
        target_v = question.versions[0]

    # Student permission check: students only see approved questions
    if current_user.role == "STUDENT" and target_v.verification_status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unverified question cannot be viewed by student",
        )

    runs = [
        {
            "run_no": r.run_no,
            "solver_model": r.solver_model,
            "answer": r.answer,
            "steps": r.steps,
            "agree": r.agree,
            "diff_notes": r.diff_notes,
        }
        for r in (target_v.verification_runs or [])
    ]

    question_data = {
        "id": question.id,
        "short_id": question.short_id,
        "long_id": question.long_id,
        "origin": question.origin,
        "source_ref": question.source_ref,
        "owner_teacher_id": question.owner_teacher_id,
        "current_version": question.current_version,
        "all_versions": [
            {
                "version": ver.version,
                "verification_status": ver.verification_status,
                "created_at": ver.created_at.isoformat(),
            }
            for ver in question.versions
        ],
        "version_data": {
            "id": target_v.id,
            "version": target_v.version,
            "body": target_v.body,
            "options": target_v.options_json,
            "answer": target_v.answer,
            "solution": target_v.solution,
            "verification_status": target_v.verification_status,
            "meta": target_v.meta_json or {},
            "verification_runs": runs,
        },
        "created_at": question.created_at.isoformat(),
    }

    if current_user.role == "STUDENT":
        question_data = question_bank_service.sanitize_for_student(question_data)

    return question_data


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_question_manual(
    payload: CreateQuestionRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Teacher/Incharge creates a teacher-authored question in the bank.
    """
    # Check duplicate
    is_dup = await question_bank_service.check_duplicate(
        db=db, body_text=payload.body, school_id=current_user.school_id
    )
    if is_dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate question detected in your school's question bank",
        )

    new_q = await question_bank_service.create_question(
        db=db,
        teacher_id=current_user.id,
        school_id=current_user.school_id,
        subject=payload.subject,
        class_level=payload.class_level,
        chapter=payload.chapter,
        topic=payload.topic,
        origin=payload.origin,
        body=payload.body,
        options=payload.options,
        answer=payload.answer,
        solution=payload.solution,
        marks=payload.marks,
        difficulty=payload.difficulty,
        question_type=payload.question_type,
        source_ref=payload.source_ref,
        verification_status=payload.verification_status,
        meta_json=payload.meta,
    )
    await db.commit()

    return {
        "id": new_q.id,
        "short_id": new_q.short_id,
        "long_id": new_q.long_id,
        "current_version": 1,
        "message": "Question successfully created",
    }


@router.post("/{qid}/versions", status_code=status.HTTP_201_CREATED)
async def create_new_question_version(
    qid: str,
    payload: EditQuestionRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Edits a question by creating a new version under the same QID.
    Rules.md B.2: IDs are immutable; edits create a new version.
    """
    try:
        new_v = await question_bank_service.create_new_version(
            db=db,
            qid=qid,
            user_id=current_user.id,
            body=payload.body,
            options=payload.options,
            answer=payload.answer,
            solution=payload.solution,
            verification_status=payload.verification_status,
            meta_json=payload.meta,
        )
        await db.commit()
        return {
            "qid": qid,
            "version": new_v.version,
            "verification_status": new_v.verification_status,
            "message": f"Created version v{new_v.version}",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{qid}/versions/{version}/status")
async def update_question_verification_status(
    qid: str,
    version: int,
    payload: QuestionStatusUpdateRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Teacher explicitly approves or flags a question version.
    Rules.md C.2: Only a teacher's explicit approval -> Approved.
    """
    stmt = select(QuestionVersion).where(
        and_(QuestionVersion.qid == qid, QuestionVersion.version == version)
    )
    res = await db.execute(stmt)
    q_ver = res.scalar_one_or_none()
    if not q_ver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question version {version} not found for QID {qid}",
        )

    q_ver.verification_status = payload.status
    await db.commit()

    return {
        "qid": qid,
        "version": version,
        "verification_status": q_ver.verification_status,
        "message": f"Status updated to {payload.status}",
    }


# --- Bookmarks, Favourites, Notes, Collections ---
@router.post("/bookmark")
async def toggle_bookmark(
    payload: BookmarkRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(Bookmark).where(
        and_(Bookmark.user_id == current_user.id, Bookmark.qid == payload.qid)
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"bookmarked": False, "qid": payload.qid}
    else:
        bm = Bookmark(user_id=current_user.id, qid=payload.qid)
        db.add(bm)
        await db.commit()
        return {"bookmarked": True, "qid": payload.qid}


@router.get("/bookmarks/list")
async def list_bookmarks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    stmt = select(Bookmark.qid).where(Bookmark.user_id == current_user.id)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/favourite")
async def toggle_favourite(
    payload: FavouriteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(Favourite).where(
        and_(Favourite.user_id == current_user.id, Favourite.qid == payload.qid)
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"favourited": False, "qid": payload.qid}
    else:
        fav = Favourite(user_id=current_user.id, qid=payload.qid)
        db.add(fav)
        await db.commit()
        return {"favourited": True, "qid": payload.qid}


@router.post("/note")
async def add_or_update_note(
    payload: QuestionNoteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(QuestionNote).where(
        and_(QuestionNote.user_id == current_user.id, QuestionNote.qid == payload.qid)
    )
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()

    if note:
        note.note_text = payload.note_text
    else:
        note = QuestionNote(
            user_id=current_user.id,
            qid=payload.qid,
            note_text=payload.note_text,
        )
        db.add(note)
    await db.commit()
    return {"qid": payload.qid, "note_text": note.note_text}


@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreateRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    col = Collection(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )
    db.add(col)
    await db.commit()
    return {"id": col.id, "name": col.name}


@router.post("/collections/items")
async def add_item_to_collection(
    payload: AddToCollectionRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    col_stmt = select(Collection).where(
        and_(Collection.id == payload.collection_id, Collection.user_id == current_user.id)
    )
    res = await db.execute(col_stmt)
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    item = CollectionItem(
        collection_id=payload.collection_id,
        qid=payload.qid,
        version=payload.version,
    )
    db.add(item)
    await db.commit()
    return {"collection_id": payload.collection_id, "qid": payload.qid}
