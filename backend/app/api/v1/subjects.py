import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_incharge
from app.core.errors import ConflictError
from app.db.models import Subject, User
from app.db.session import get_db
from app.schemas import SubjectCreateRequest, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectResponse])
async def list_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if not school_id:
        return []

    stmt = select(Subject).where(Subject.school_id == school_id).order_by(Subject.name.asc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    req: SubjectCreateRequest,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id

    existing = await db.execute(
        select(Subject).where(
            Subject.school_id == school_id,
            Subject.code == req.code.strip().upper(),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Subject with code '{req.code}' already exists in this school")

    subject = Subject(
        id=str(uuid.uuid4()),
        school_id=school_id,
        name=req.name.strip(),
        code=req.code.strip().upper(),
    )
    db.add(subject)
    await db.commit()
    await db.refresh(subject)

    return subject
