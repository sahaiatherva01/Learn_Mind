from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.core.errors import NotFoundError
from app.core.security import SchoolStatus, UserRole
from app.db.models import School, User
from app.db.session import get_db
from app.schemas import ApprovalActionRequest, SchoolResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/schools", response_model=list[SchoolResponse])
async def list_schools(
    status_filter: str | None = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(School)
    if status_filter:
        stmt = stmt.where(School.status == status_filter.upper())
    stmt = stmt.order_by(School.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/schools/{school_id}/approve", response_model=SchoolResponse)
async def approve_school(
    school_id: str,
    req: ApprovalActionRequest | None = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(School).where(School.id == school_id))
    school = res.scalar_one_or_none()
    if not school:
        raise NotFoundError(f"School {school_id} not found")

    school.status = SchoolStatus.APPROVED.value
    school.approved_by_admin_id = current_user.id
    await db.commit()
    await db.refresh(school)
    return school


@router.post("/schools/{school_id}/reject", response_model=SchoolResponse)
async def reject_school(
    school_id: str,
    req: ApprovalActionRequest | None = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(School).where(School.id == school_id))
    school = res.scalar_one_or_none()
    if not school:
        raise NotFoundError(f"School {school_id} not found")

    school.status = SchoolStatus.REJECTED.value
    await db.commit()
    await db.refresh(school)
    return school


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_schools = await db.scalar(select(func.count(School.id)))
    pending_schools = await db.scalar(
        select(func.count(School.id)).where(School.status == SchoolStatus.PENDING_APPROVAL.value)
    )
    total_users = await db.scalar(select(func.count(User.id)))
    total_teachers = await db.scalar(
        select(func.count(User.id)).where(
            User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value])
        )
    )
    total_students = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.STUDENT.value)
    )

    return {
        "stats": {
            "total_schools": total_schools or 0,
            "pending_schools": pending_schools or 0,
            "total_users": total_users or 0,
            "total_teachers": total_teachers or 0,
            "total_students": total_students or 0,
        },
        "system": {
            "version": "1.0.0",
            "environment": "production-ready",
        },
    }
