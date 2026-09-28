from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import (
    User,
    Section,
    Subject,
    TeacherAssignment,
    StudentEnrollment,
    FileRecord,
    Question,
)
from app.schemas import (
    StudentEnrollmentResponse,
    TeacherAssignmentResponse,
)
from app.core.security import (
    UserRole,
    EnrollmentStatus,
)
from app.core.errors import NotFoundError, ForbiddenError
from app.core.dependencies import require_teacher, require_class_teacher

router = APIRouter(prefix="/teacher", tags=["Teacher"])


@router.get("/dashboard")
async def get_teacher_dashboard(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # 1. Fetch teacher assignments
    assign_stmt = (
        select(TeacherAssignment, Section, Subject)
        .join(Section, TeacherAssignment.section_id == Section.id)
        .join(Subject, TeacherAssignment.subject_id == Subject.id)
        .where(TeacherAssignment.teacher_id == current_user.id)
    )
    assign_res = await db.execute(assign_stmt)
    assignments = []
    section_ids = set()
    for assign, sec, subj in assign_res.all():
        section_ids.add(sec.id)
        assignments.append({
            "id": assign.id,
            "section_id": sec.id,
            "section_name": sec.section_name,
            "class_level": sec.class_level,
            "subject_id": subj.id,
            "subject_name": subj.name,
            "subject_code": subj.code,
        })

    # 2. Check if class teacher of any sections
    class_sec_stmt = select(Section).where(Section.class_teacher_id == current_user.id)
    class_sec_res = await db.execute(class_sec_stmt)
    class_sections = class_sec_res.scalars().all()
    class_section_ids = [s.id for s in class_sections]

    # 3. Count pending student enrollments for class teacher's sections
    pending_enrollments_count = 0
    if class_section_ids:
        pending_enrollments_count = await db.scalar(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.section_id.in_(class_section_ids),
                StudentEnrollment.status == EnrollmentStatus.PENDING_APPROVAL.value,
            )
        ) or 0

    # 4. Count enrolled students across assigned sections
    all_monitored_sections = list(section_ids.union(set(class_section_ids)))
    student_count = 0
    if all_monitored_sections:
        student_count = await db.scalar(
            select(func.count(StudentEnrollment.id)).where(
                StudentEnrollment.section_id.in_(all_monitored_sections),
                StudentEnrollment.status == EnrollmentStatus.APPROVED.value,
            )
        ) or 0

    # 5. Teacher's private library files count
    library_files_count = await db.scalar(
        select(func.count(FileRecord.id)).where(FileRecord.teacher_id == current_user.id)
    ) or 0

    # 6. Teacher's authored/saved questions count
    questions_count = await db.scalar(
        select(func.count(Question.id)).where(Question.owner_teacher_id == current_user.id)
    ) or 0

    return {
        "teacher": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
        },
        "stats": {
            "assigned_classes_count": len(section_ids),
            "class_teacher_sections_count": len(class_sections),
            "total_students_count": student_count,
            "pending_enrollment_requests": pending_enrollments_count,
            "library_files_count": library_files_count,
            "questions_count": questions_count,
        },
        "assignments": assignments,
        "class_teacher_sections": [
            {
                "id": s.id,
                "section_name": s.section_name,
                "class_level": s.class_level,
            }
            for s in class_sections
        ],
    }


@router.get("/assignments", response_model=List[TeacherAssignmentResponse])
async def get_teacher_assignments(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(TeacherAssignment, Section, Subject)
        .join(Section, TeacherAssignment.section_id == Section.id)
        .join(Subject, TeacherAssignment.subject_id == Subject.id)
        .where(TeacherAssignment.teacher_id == current_user.id)
    )
    res = await db.execute(stmt)
    rows = res.all()

    return [
        TeacherAssignmentResponse(
            id=assign.id,
            teacher_id=current_user.id,
            teacher_name=current_user.full_name,
            section_id=sec.id,
            section_name=sec.section_name,
            class_level=sec.class_level,
            subject_id=subj.id,
            subject_name=subj.name,
            created_at=assign.created_at,
        )
        for assign, sec, subj in rows
    ]


@router.get("/students")
async def list_students_roster(
    section_id: Optional[str] = None,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Basic roster lookup school-wide (PRD §6 assumption)
    stmt = (
        select(User, StudentEnrollment, Section)
        .outerjoin(StudentEnrollment, StudentEnrollment.student_id == User.id)
        .outerjoin(Section, StudentEnrollment.section_id == Section.id)
        .where(
            User.school_id == current_user.school_id,
            User.role == UserRole.STUDENT.value,
        )
    )
    if section_id:
        stmt = stmt.where(StudentEnrollment.section_id == section_id)

    stmt = stmt.order_by(User.full_name.asc())
    res = await db.execute(stmt)
    rows = res.all()

    students = []
    for user, enrollment, section in rows:
        students.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "roll_number": user.roll_number,
            "school_code": user.school_code,
            "section": {
                "id": section.id,
                "section_name": section.section_name,
                "class_level": section.class_level,
                "enrollment_status": enrollment.status if enrollment else None,
            }
            if section
            else None,
        })
    return students


@router.get("/enrollments", response_model=List[StudentEnrollmentResponse])
async def list_class_teacher_enrollments(
    current_user: User = Depends(require_class_teacher),
    db: AsyncSession = Depends(get_db),
):
    # If incharge or admin, can see all enrollments
    if current_user.role in [UserRole.ADMIN.value, UserRole.INCHARGE.value]:
        stmt = (
            select(StudentEnrollment, User, Section)
            .join(User, StudentEnrollment.student_id == User.id)
            .join(Section, StudentEnrollment.section_id == Section.id)
            .where(
                Section.school_id == current_user.school_id,
                StudentEnrollment.status == EnrollmentStatus.PENDING_APPROVAL.value,
            )
        )
    else:
        # Class teacher only sees pending enrollments for their designated section
        stmt = (
            select(StudentEnrollment, User, Section)
            .join(User, StudentEnrollment.student_id == User.id)
            .join(Section, StudentEnrollment.section_id == Section.id)
            .where(
                Section.class_teacher_id == current_user.id,
                StudentEnrollment.status == EnrollmentStatus.PENDING_APPROVAL.value,
            )
        )

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
async def class_teacher_approve_enrollment(
    enrollment_id: str,
    current_user: User = Depends(require_class_teacher),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(StudentEnrollment, User, Section)
        .join(User, StudentEnrollment.student_id == User.id)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(StudentEnrollment.id == enrollment_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise NotFoundError(f"Enrollment request {enrollment_id} not found")

    enrollment, user, section = row

    # Check permission: must be incharge/admin OR the designated class teacher of this section
    if current_user.role not in [UserRole.ADMIN.value, UserRole.INCHARGE.value]:
        if section.class_teacher_id != current_user.id:
            raise ForbiddenError("Only the Class Teacher of this section or an Incharge can approve this enrollment")

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
async def class_teacher_reject_enrollment(
    enrollment_id: str,
    current_user: User = Depends(require_class_teacher),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(StudentEnrollment, User, Section)
        .join(User, StudentEnrollment.student_id == User.id)
        .join(Section, StudentEnrollment.section_id == Section.id)
        .where(StudentEnrollment.id == enrollment_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise NotFoundError(f"Enrollment request {enrollment_id} not found")

    enrollment, user, section = row

    if current_user.role not in [UserRole.ADMIN.value, UserRole.INCHARGE.value]:
        if section.class_teacher_id != current_user.id:
            raise ForbiddenError("Only the Class Teacher of this section or an Incharge can reject this enrollment")

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
