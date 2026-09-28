from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---
class RegisterSchoolRequest(BaseModel):
    school_name: str = Field(..., min_length=2, max_length=255)
    school_code: str = Field(..., min_length=2, max_length=50)
    board: str = Field(default="ICSE_ISC")
    admin_name: str = Field(..., min_length=2, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=6)
    wing_name: Optional[str] = "Main Wing"


class RegisterTeacherRequest(BaseModel):
    school_code: str
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    role: str = Field(default="SUBJECT_TEACHER")  # SUBJECT_TEACHER or CLASS_TEACHER


class RegisterStudentRequest(BaseModel):
    school_code: str
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    roll_number: Optional[str] = None
    teacher_code: Optional[str] = None
    section_id: Optional[str] = None


class LoginRequest(BaseModel):
    # Method 1: email + password
    email: Optional[EmailStr] = None
    # Method 2: roll_number + school_code + password
    roll_number: Optional[str] = None
    school_code: Optional[str] = None
    # Method 3: teacher_code + password
    teacher_code: Optional[str] = None

    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    email: Optional[str] = None
    roll_number: Optional[str] = None
    school_code: Optional[str] = None
    teacher_code: Optional[str] = None
    full_name: str
    role: str
    status: str
    created_at: datetime


class StudentProfileResponse(BaseModel):
    id: str
    full_name: str
    roll_number: Optional[str] = None
    school_name: Optional[str] = None
    school_code: Optional[str] = None
    section_id: Optional[str] = None
    section_name: Optional[str] = None
    class_level: Optional[int] = None
    enrollment_status: Optional[str] = None


# --- School Schemas ---
class SchoolResponse(BaseModel):
    id: str
    name: str
    code: str
    board: str
    status: str
    created_at: datetime
    updated_at: datetime


class SectionCreateRequest(BaseModel):
    class_level: int = Field(..., ge=6, le=12)
    section_name: str = Field(..., min_length=1, max_length=50)
    class_teacher_id: Optional[str] = None


class SectionResponse(BaseModel):
    id: str
    school_id: str
    class_level: int
    section_name: str
    class_teacher_id: Optional[str] = None
    class_teacher_name: Optional[str] = None
    created_at: datetime


class SubjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)


class SubjectResponse(BaseModel):
    id: str
    school_id: str
    name: str
    code: str
    created_at: datetime


class TeacherAssignmentRequest(BaseModel):
    teacher_id: str
    section_id: str
    subject_id: str


class TeacherAssignmentResponse(BaseModel):
    id: str
    teacher_id: str
    teacher_name: Optional[str] = None
    section_id: str
    section_name: Optional[str] = None
    class_level: Optional[int] = None
    subject_id: str
    subject_name: Optional[str] = None
    created_at: datetime


class StudentEnrollmentResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    student_email: Optional[str] = None
    roll_number: Optional[str] = None
    section_id: str
    section_name: str
    class_level: int
    status: str
    requested_at: datetime
    reviewed_at: Optional[datetime] = None


class ApprovalActionRequest(BaseModel):
    role: Optional[str] = None  # e.g., for teacher approval: CLASS_TEACHER or SUBJECT_TEACHER
    reason: Optional[str] = None
