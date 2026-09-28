from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import (
    School,
    User,
    Section,
    Subject,
    StudentEnrollment,
    TeacherAssignment,
)
from app.schemas import (
    UserResponse,
    StudentEnrollmentResponse,
    ApprovalActionRequest,
)
from app.core.security import (
    UserRole,
    UserStatus,
    EnrollmentStatus,
)
from app.core.errors import NotFoundError, ValidationError, ForbiddenError
from app.core.dependencies import require_incharge

router = APIRouter(prefix="/incharge", tags=["Incharge"])


@router.get("/teachers", response_model=List[UserResponse])
async def list_school_teachers(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.school_id:
        raise ForbiddenError("Incharge must be associated with a school")

    stmt = select(User).where(
        User.school_id == current_user.school_id,
        User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]),
    )
    if status_filter:
        stmt = stmt.where(User.status == status_filter.upper())
    stmt = stmt.order_by(User.created_at.desc())
    res = await db.execute(stmt)
    teachers = res.scalars().all()

    # Get school name
    school_name = None
    if current_user.school_id:
        s_res = await db.execute(select(School).where(School.id == current_user.school_id))
        school = s_res.scalar_one_or_none()
        if school:
            school_name = school.name

    return [
        UserResponse(
            id=t.id,
            school_id=t.school_id,
            school_name=school_name,
            email=t.email,
            roll_number=t.roll_number,
            school_code=t.school_code,
            teacher_code=t.teacher_code,
            full_name=t.full_name,
            role=t.role,
            status=t.status,
            created_at=t.created_at,
        )
        for t in teachers
    ]


@router.post("/teachers/{teacher_id}/approve", response_model=UserResponse)
async def approve_teacher(
    teacher_id: str,
    req: Optional[ApprovalActionRequest] = None,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(
        User.id == teacher_id,
        User.school_id == current_user.school_id,
        User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]),
    )
    res = await db.execute(stmt)
    teacher = res.scalar_one_or_none()
    if not teacher:
        raise NotFoundError(f"Teacher {teacher_id} not found in this school")

    teacher.status = UserStatus.ACTIVE.value
    if req and req.role:
        if req.role in [UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]:
            teacher.role = req.role

    await db.commit()
    await db.refresh(teacher)

    return UserResponse(
        id=teacher.id,
        school_id=teacher.school_id,
        school_name=None,
        email=teacher.email,
        roll_number=teacher.roll_number,
        school_code=teacher.school_code,
        teacher_code=teacher.teacher_code,
        full_name=teacher.full_name,
        role=teacher.role,
        status=teacher.status,
        created_at=teacher.created_at,
    )


@router.post("/teachers/{teacher_id}/reject", response_model=UserResponse)
async def reject_teacher(
    teacher_id: str,
    req: Optional[ApprovalActionRequest] = None,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(
        User.id == teacher_id,
        User.school_id == current_user.school_id,
        User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]),
    )
    res = await db.execute(stmt)
    teacher = res.scalar_one_or_none()
    if not teacher:
        raise NotFoundError(f"Teacher {teacher_id} not found in this school")

    teacher.status = UserStatus.REJECTED.value
    await db.commit()
    await db.refresh(teacher)

    return UserResponse(
        id=teacher.id,
        school_id=teacher.school_id,
        school_name=None,
        email=teacher.email,
        roll_number=teacher.roll_number,
        school_code=teacher.school_code,
        teacher_code=teacher.teacher_code,
        full_name=teacher.full_name,
        role=teacher.role,
        status=teacher.status,
        created_at=teacher.created_at,
    )


@router.get("/enrollments", response_model=List[StudentEnrollmentResponse])
async def list_student_enrollments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(StudentEnrollment, User, Section)
        .join(User, StudentEnrollment.student_id == User.id)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(Section.school_id == current_user.school_id)
    )
    if status_filter:
        stmt = stmt.where(StudentEnrollment.status == status_filter.upper())
    stmt = stmt.order_by(StudentEnrollment.requested_at.desc())

    res = await db.execute(stmt)
    rows = res.all()

    return [
        StudentEnrollmentResponse(
            id=enr.id,
            student_id=usr.id,
            student_name=usr.full_name,
            student_email=usr.email,
            roll_number=usr.roll_number,
            section_id=sec.id,
            section_name=sec.section_name,
            class_level=sec.class_level,
            status=enr.status,
            requested_at=enr.requested_at,
            reviewed_at=enr.reviewed_at,
        )
        for enr, usr, sec in rows
    ]


@router.post("/enrollments/{enrollment_id}/approve", response_model=StudentEnrollmentResponse)
async def approve_student_enrollment(
    enrollment_id: str,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(StudentEnrollment, User, Section)
        .join(User, StudentEnrollment.student_id == User.id)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(
            StudentEnrollment.id == enrollment_id,
            Section.school_id == current_user.school_id,
        )
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise NotFoundError(f"Enrollment request {enrollment_id} not found")

    enrollment, user, section = row
    enrollment.status = EnrollmentStatus.APPROVED.value
    enrollment.approved_by_id = current_user.id
    enrollment.reviewed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(enrollment)

    return StudentEnrollmentResponse(
        id=enrollment.id,
        student_id=user.id,
        student_name=user.full_name,
        student_email=user.email,
        roll_number=user.roll_number,
        section_id=section.id,
        section_name=section.section_name,
        class_level=section.class_level,
        status=enrollment.status,
        requested_at=enrollment.requested_at,
        reviewed_at=enrollment.reviewed_at,
    )


@router.post("/enrollments/{enrollment_id}/reject", response_model=StudentEnrollmentResponse)
async def reject_student_enrollment(
    enrollment_id: str,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(StudentEnrollment, User, Section)
        .join(User, StudentEnrollment.student_id == User.id)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(
            StudentEnrollment.id == enrollment_id,
            Section.school_id == current_user.school_id,
        )
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise NotFoundError(f"Enrollment request {enrollment_id} not found")

    enrollment, user, section = row
    enrollment.status = EnrollmentStatus.REJECTED.value
    enrollment.approved_by_id = current_user.id
    enrollment.reviewed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(enrollment)

    return StudentEnrollmentResponse(
        id=enrollment.id,
        student_id=user.id,
        student_name=user.full_name,
        student_email=user.email,
        roll_number=user.roll_number,
        section_id=section.id,
        section_name=section.section_name,
        class_level=section.class_level,
        status=enrollment.status,
        requested_at=enrollment.requested_at,
        reviewed_at=enrollment.reviewed_at,
    )


@router.get("/dashboard")
async def get_incharge_dashboard(
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id

    pending_teachers_count = await db.scalar(
        select(func.count(User.id)).where(
            User.school_id == school_id,
            User.status == UserStatus.PENDING_APPROVAL.value,
            User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]),
        )
    )

    active_teachers_count = await db.scalar(
        select(func.count(User.id)).where(
            User.school_id == school_id,
            User.status == UserStatus.ACTIVE.value,
            User.role.in_([UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]),
        )
    )

    pending_enrollments_count = await db.scalar(
        select(func.count(StudentEnrollment.id))
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(
            Section.school_id == school_id,
            StudentEnrollment.status == EnrollmentStatus.PENDING_APPROVAL.value,
        )
    )

    total_sections_count = await db.scalar(
        select(func.count(Section.id)).where(Section.school_id == school_id)
    )

    total_subjects_count = await db.scalar(
        select(func.count(Subject.id)).where(Subject.school_id == school_id)
    )

    return {
        "stats": {
            "pending_teacher_approvals": pending_teachers_count or 0,
            "active_teachers": active_teachers_count or 0,
            "pending_student_enrollments": pending_enrollments_count or 0,
            "total_sections": total_sections_count or 0,
            "total_subjects": total_subjects_count or 0,
        }
    }
