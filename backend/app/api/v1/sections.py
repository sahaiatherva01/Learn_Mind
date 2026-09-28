from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import (
    User,
    Section,
    Subject,
    TeacherAssignment,
)
from app.schemas import (
    SectionCreateRequest,
    SectionResponse,
    TeacherAssignmentRequest,
    TeacherAssignmentResponse,
)
from app.core.security import UserRole, UserStatus
from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.core.dependencies import get_current_user, require_incharge
import uuid

router = APIRouter(prefix="/sections", tags=["Sections"])


@router.get("", response_model=List[SectionResponse])
async def list_sections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if not school_id:
        return []

    stmt = (
        select(Section, User)
        .outerjoin(User, Section.class_teacher_id == User.id)
        .where(Section.school_id == school_id)
        .order_by(Section.class_level.asc(), Section.section_name.asc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    return [
        SectionResponse(
            id=sec.id,
            school_id=sec.school_id,
            class_level=sec.class_level,
            section_name=sec.section_name,
            class_teacher_id=sec.class_teacher_id,
            class_teacher_name=teacher.full_name if teacher else None,
            created_at=sec.created_at,
        )
        for sec, teacher in rows
    ]


@router.post("", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    req: SectionCreateRequest,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id

    # Check unique constraint
    existing = await db.execute(
        select(Section).where(
            Section.school_id == school_id,
            Section.class_level == req.class_level,
            Section.section_name == req.section_name.strip(),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Section '{req.section_name}' already exists for Class {req.class_level}"
        )

    class_teacher_name = None
    if req.class_teacher_id:
        t_res = await db.execute(
            select(User).where(
                User.id == req.class_teacher_id,
                User.school_id == school_id,
            )
        )
        teacher = t_res.scalar_one_or_none()
        if not teacher:
            raise NotFoundError(f"Teacher {req.class_teacher_id} not found in this school")
        class_teacher_name = teacher.full_name

    section = Section(
        id=str(uuid.uuid4()),
        school_id=school_id,
        class_level=req.class_level,
        section_name=req.section_name.strip(),
        class_teacher_id=req.class_teacher_id,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)

    return SectionResponse(
        id=section.id,
        school_id=section.school_id,
        class_level=section.class_level,
        section_name=section.section_name,
        class_teacher_id=section.class_teacher_id,
        class_teacher_name=class_teacher_name,
        created_at=section.created_at,
    )


@router.post("/assign-teacher", response_model=TeacherAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_teacher_to_section(
    req: TeacherAssignmentRequest,
    current_user: User = Depends(require_incharge),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id

    # Validate Teacher
    t_res = await db.execute(
        select(User).where(
            User.id == req.teacher_id,
            User.school_id == school_id,
        )
    )
    teacher = t_res.scalar_one_or_none()
    if not teacher:
        raise NotFoundError("Teacher not found")

    # Validate Section
    sec_res = await db.execute(
        select(Section).where(
            Section.id == req.section_id,
            Section.school_id == school_id,
        )
    )
    section = sec_res.scalar_one_or_none()
    if not section:
        raise NotFoundError("Section not found")

    # Validate Subject
    sub_res = await db.execute(
        select(Subject).where(
            Subject.id == req.subject_id,
            Subject.school_id == school_id,
        )
    )
    subject = sub_res.scalar_one_or_none()
    if not subject:
        raise NotFoundError("Subject not found")

    # Check duplicate assignment
    existing_res = await db.execute(
        select(TeacherAssignment).where(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.section_id == section.id,
            TeacherAssignment.subject_id == subject.id,
        )
    )
    existing = existing_res.scalar_one_or_none()
    if existing:
        raise ConflictError("This teacher is already assigned to this subject and section")

    assignment = TeacherAssignment(
        id=str(uuid.uuid4()),
        teacher_id=teacher.id,
        section_id=section.id,
        subject_id=subject.id,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return TeacherAssignmentResponse(
        id=assignment.id,
        teacher_id=teacher.id,
        teacher_name=teacher.full_name,
        section_id=section.id,
        section_name=section.section_name,
        class_level=section.class_level,
        subject_id=subject.id,
        subject_name=subject.name,
        created_at=assignment.created_at,
    )
