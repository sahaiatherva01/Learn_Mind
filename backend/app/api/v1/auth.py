import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import (
    EnrollmentStatus,
    SchoolStatus,
    UserRole,
    UserStatus,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.models import (
    Incharge,
    School,
    Section,
    StudentEnrollment,
    Subject,
    TeacherAssignment,
    User,
)
from app.db.session import get_db
from app.schemas import (
    LoginRequest,
    RegisterSchoolRequest,
    RegisterStudentRequest,
    RegisterTeacherRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-school", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_school(
    req: RegisterSchoolRequest,
    db: AsyncSession = Depends(get_db),
):
    # Check if school code exists
    existing_school = await db.execute(
        select(School).where(School.code == req.school_code.strip().upper())
    )
    if existing_school.scalar_one_or_none():
        raise ConflictError(f"School code '{req.school_code}' already exists")

    # Check if admin email exists
    existing_user = await db.execute(
        select(User).where(User.email == req.admin_email.strip().lower())
    )
    if existing_user.scalar_one_or_none():
        raise ConflictError(f"Email '{req.admin_email}' is already registered")

    # Create School (status is PENDING_APPROVAL for production; if it's the first platform admin it can be pre-approved)
    school = School(
        id=str(uuid.uuid4()),
        name=req.school_name.strip(),
        code=req.school_code.strip().upper(),
        board=req.board,
        status=SchoolStatus.APPROVED.value,  # approved on creation by default in dev/single-school setup
    )
    db.add(school)

    # Create Admin/Incharge user
    user = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=req.admin_email.strip().lower(),
        school_code=school.code,
        full_name=req.admin_name.strip(),
        password_hash=get_password_hash(req.admin_password),
        role=UserRole.INCHARGE.value,  # Incharge of the school
        status=UserStatus.ACTIVE.value,
    )
    db.add(user)

    # Create Incharge profile
    incharge = Incharge(
        id=str(uuid.uuid4()),
        user_id=user.id,
        school_id=school.id,
        wing_name=req.wing_name or "Main Wing",
        can_approve_teachers=True,
        can_approve_students=True,
    )
    db.add(incharge)

    await db.commit()
    await db.refresh(user)
    await db.refresh(school)

    token = create_access_token(
        subject=user.id,
        role=user.role,
        school_id=school.id,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            school_id=school.id,
            school_name=school.name,
            email=user.email,
            school_code=school.code,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        ),
    )


@router.post("/register-teacher", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_teacher(
    req: RegisterTeacherRequest,
    db: AsyncSession = Depends(get_db),
):
    school_result = await db.execute(
        select(School).where(School.code == req.school_code.strip().upper())
    )
    school = school_result.scalar_one_or_none()
    if not school:
        raise NotFoundError(f"School with code '{req.school_code}' not found")

    user_result = await db.execute(select(User).where(User.email == req.email.strip().lower()))
    if user_result.scalar_one_or_none():
        raise ConflictError(f"Email '{req.email}' is already registered")

    role_val = (
        UserRole.CLASS_TEACHER.value
        if req.role == UserRole.CLASS_TEACHER.value
        else UserRole.SUBJECT_TEACHER.value
    )

    user = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=req.email.strip().lower(),
        school_code=school.code,
        full_name=req.full_name.strip(),
        password_hash=get_password_hash(req.password),
        role=role_val,
        status=UserStatus.PENDING_APPROVAL.value,  # Requires incharge approval
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        school_id=school.id,
        school_name=school.name,
        email=user.email,
        school_code=school.code,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
    )


@router.post("/register-student", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_student(
    req: RegisterStudentRequest,
    db: AsyncSession = Depends(get_db),
):
    school_result = await db.execute(
        select(School).where(School.code == req.school_code.strip().upper())
    )
    school = school_result.scalar_one_or_none()
    if not school:
        raise NotFoundError(f"School with code '{req.school_code}' not found")

    # Validate that at least one identifier is provided (email, roll_number, or teacher_code)
    if not req.email and not req.roll_number and not req.teacher_code:
        raise ValidationError("Provide at least an email, roll number, or teacher-issued code")

    # Check email conflict if provided
    if req.email:
        email_clean = req.email.strip().lower()
        existing = await db.execute(select(User).where(User.email == email_clean))
        if existing.scalar_one_or_none():
            raise ConflictError(f"Email '{req.email}' is already registered")
    else:
        email_clean = None

    # Check roll number conflict within same school
    if req.roll_number:
        roll_clean = req.roll_number.strip().upper()
        existing = await db.execute(
            select(User).where(
                User.school_id == school.id,
                User.roll_number == roll_clean,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(
                f"Roll number '{req.roll_number}' already registered in this school"
            )
    else:
        roll_clean = None

    # Check teacher code if provided
    teacher_code_clean = req.teacher_code.strip().upper() if req.teacher_code else None
    if teacher_code_clean:
        existing = await db.execute(
            select(User).where(
                User.school_id == school.id,
                User.teacher_code == teacher_code_clean,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Teacher-issued code has already been claimed")

    student = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=email_clean,
        roll_number=roll_clean,
        school_code=school.code,
        teacher_code=teacher_code_clean,
        full_name=req.full_name.strip(),
        password_hash=get_password_hash(req.password),
        role=UserRole.STUDENT.value,
        status=UserStatus.ACTIVE.value,  # Student account is active, section enrollment is pending
    )
    db.add(student)

    # If section_id provided, create pending enrollment request
    if req.section_id:
        sec_res = await db.execute(
            select(Section).where(
                Section.id == req.section_id,
                Section.school_id == school.id,
            )
        )
        section = sec_res.scalar_one_or_none()
        if section:
            enrollment = StudentEnrollment(
                id=str(uuid.uuid4()),
                student_id=student.id,
                section_id=section.id,
                roll_number=roll_clean,
                status=EnrollmentStatus.PENDING_APPROVAL.value,
            )
            db.add(enrollment)

    await db.commit()
    await db.refresh(student)

    token = create_access_token(
        subject=student.id,
        role=student.role,
        school_id=school.id,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=student.id,
            school_id=school.id,
            school_name=school.name,
            email=student.email,
            roll_number=student.roll_number,
            school_code=school.code,
            teacher_code=student.teacher_code,
            full_name=student.full_name,
            role=student.role,
            status=student.status,
            created_at=student.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = None

    # Method 1: Email
    if req.email:
        res = await db.execute(select(User).where(User.email == req.email.strip().lower()))
        user = res.scalar_one_or_none()

    # Method 2: Roll Number + School Code
    elif req.roll_number and req.school_code:
        school_res = await db.execute(
            select(School).where(School.code == req.school_code.strip().upper())
        )
        school = school_res.scalar_one_or_none()
        if school:
            res = await db.execute(
                select(User).where(
                    User.school_id == school.id,
                    User.roll_number == req.roll_number.strip().upper(),
                )
            )
            user = res.scalar_one_or_none()

    # Method 3: Teacher-issued code
    elif req.teacher_code:
        res = await db.execute(
            select(User).where(User.teacher_code == req.teacher_code.strip().upper())
        )
        user = res.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("Invalid login credentials")

    if not verify_password(req.password, user.password_hash):
        raise UnauthorizedError("Invalid login credentials")

    # Fetch school name
    school_name = None
    if user.school_id:
        school_res = await db.execute(select(School).where(School.id == user.school_id))
        school = school_res.scalar_one_or_none()
        if school:
            school_name = school.name

    token = create_access_token(
        subject=user.id,
        role=user.role,
        school_id=user.school_id,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            school_id=user.school_id,
            school_name=school_name,
            email=user.email,
            roll_number=user.roll_number,
            school_code=user.school_code,
            teacher_code=user.teacher_code,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        ),
    )


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    school_name = None
    if current_user.school_id:
        s_res = await db.execute(select(School).where(School.id == current_user.school_id))
        school = s_res.scalar_one_or_none()
        if school:
            school_name = school.name

    profile_data = {
        "id": current_user.id,
        "school_id": current_user.school_id,
        "school_name": school_name,
        "email": current_user.email,
        "roll_number": current_user.roll_number,
        "school_code": current_user.school_code,
        "teacher_code": current_user.teacher_code,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "status": current_user.status,
        "created_at": current_user.created_at,
    }

    # If student, attach enrollment status and enrolled section (field-level filtering: no teacher internals)
    if current_user.role == UserRole.STUDENT.value:
        enr_res = await db.execute(
            select(StudentEnrollment, Section)
            .join(Section, StudentEnrollment.section_id == Section.id)
            .where(StudentEnrollment.student_id == current_user.id)
        )
        enr_row = enr_res.first()
        if enr_row:
            enrollment, section = enr_row
            profile_data["enrollment"] = {
                "id": enrollment.id,
                "status": enrollment.status,
                "section_id": section.id,
                "section_name": section.section_name,
                "class_level": section.class_level,
            }
        else:
            profile_data["enrollment"] = None

    # If teacher, attach assigned sections and subjects
    elif current_user.role in [UserRole.CLASS_TEACHER.value, UserRole.SUBJECT_TEACHER.value]:
        assign_res = await db.execute(
            select(TeacherAssignment, Section, Subject)
            .join(Section, TeacherAssignment.section_id == Section.id)
            .join(Subject, TeacherAssignment.subject_id == Subject.id)
            .where(TeacherAssignment.teacher_id == current_user.id)
        )
        assignments = []
        for assign, sec, subj in assign_res.all():
            assignments.append(
                {
                    "assignment_id": assign.id,
                    "section_id": sec.id,
                    "section_name": sec.section_name,
                    "class_level": sec.class_level,
                    "subject_id": subj.id,
                    "subject_name": subj.name,
                    "subject_code": subj.code,
                }
            )
        profile_data["assignments"] = assignments

    return profile_data
