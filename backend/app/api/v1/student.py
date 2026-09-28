from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import (
    User,
    School,
    Section,
    Subject,
    TeacherAssignment,
    StudentEnrollment,
    Bookmark,
    Attempt,
)
from app.schemas import StudentEnrollmentResponse
from app.core.security import (
    UserRole,
    EnrollmentStatus,
)
from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.core.dependencies import require_student
import uuid

router = APIRouter(prefix="/student", tags=["Student"])


class EnrollmentRequestBody(BaseModel):
    section_id: str


@router.get("/dashboard")
async def get_student_dashboard(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    # 1. Fetch student enrollment details
    enr_stmt = (
        select(StudentEnrollment, Section, School)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .join(School, Section.school_id == School.id)
        .where(StudentEnrollment.student_id == current_user.id)
    )
    enr_res = await db.execute(enr_stmt)
    enr_row = enr_res.first()

    section_data = None
    subjects = []
    if enr_row:
        enrollment, section, school = enr_row
        section_data = {
            "enrollment_id": enrollment.id,
            "status": enrollment.status,
            "section_id": section.id,
            "section_name": section.section_name,
            "class_level": section.class_level,
            "school_name": school.name,
            "school_code": school.code,
        }

        # If enrolled and approved, fetch the subjects taught in this section
        if enrollment.status == EnrollmentStatus.APPROVED.value:
            subj_stmt = (
                select(Subject)
                .join(TeacherAssignment, TeacherAssignment.subject_id == Subject.id)
                .where(TeacherAssignment.section_id == section.id)
                .distinct()
            )
            subj_res = await db.execute(subj_stmt)
            subjects = [
                {"id": s.id, "name": s.name, "code": s.code}
                for s in subj_res.scalars().all()
            ]

    # 2. Bookmarks count
    bookmarks_count = await db.scalar(
        select(func.count(Bookmark.id)).where(Bookmark.user_id == current_user.id)
    ) or 0

    # 3. Tests / attempts summary
    attempts_count = await db.scalar(
        select(func.count(Attempt.id)).where(Attempt.student_id == current_user.id)
    ) or 0

    return {
        "student": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "roll_number": current_user.roll_number,
        },
        "enrollment": section_data,
        "subjects": subjects,
        "stats": {
            "bookmarks_count": bookmarks_count,
            "tests_attempted": attempts_count,
            "weak_topics_count": 0,
        },
        "upcoming_tests": [],
        "weak_topics": [],
        "recent_practice": [],
    }


@router.post("/request-enrollment", response_model=StudentEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def request_section_enrollment(
    req: EnrollmentRequestBody,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    # Check section exists
    sec_stmt = select(Section).where(Section.id == req.section_id)
    sec_res = await db.execute(sec_stmt)
    section = sec_res.scalar_one_or_none()
    if not section:
        raise NotFoundError(f"Section {req.section_id} not found")

    # Check if student already has a pending or approved enrollment
    existing_stmt = select(StudentEnrollment).where(
        StudentEnrollment.student_id == current_user.id
    )
    existing_res = await db.execute(existing_stmt)
    existing = existing_res.scalar_one_or_none()

    if existing:
        if existing.status == EnrollmentStatus.APPROVED.value:
            raise ConflictError("You are already enrolled in an approved section")
        # Update existing request to new section
        existing.section_id = section.id
        existing.status = EnrollmentStatus.PENDING_APPROVAL.value
        existing.requested_at = datetime.now(timezone.utc)
        enrollment = existing
    else:
        enrollment = StudentEnrollment(
            id=str(uuid.uuid4()),
            student_id=current_user.id,
            section_id=section.id,
            roll_number=current_user.roll_number,
            status=EnrollmentStatus.PENDING_APPROVAL.value,
        )
        db.add(enrollment)

    await db.commit()
    await db.refresh(enrollment)

    return StudentEnrollmentResponse(
        id=enrollment.id,
        student_id=current_user.id,
        student_name=current_user.full_name,
        student_email=current_user.email,
        roll_number=current_user.roll_number,
        section_id=section.id,
        section_name=section.section_name,
        class_level=section.class_level,
        status=enrollment.status,
        requested_at=enrollment.requested_at,
        reviewed_at=enrollment.reviewed_at,
    )
