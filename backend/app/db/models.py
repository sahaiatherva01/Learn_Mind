import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Float,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    board: Mapped[str] = mapped_column(String(50), default="ICSE_ISC")
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", index=True)
    approved_by_admin_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    users: Mapped[List["User"]] = relationship("User", back_populates="school")
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="school")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="school")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    school_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    school_code: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    teacher_code: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    school: Mapped[Optional["School"]] = relationship("School", back_populates="users")
    incharge_profile: Mapped[Optional["Incharge"]] = relationship(
        "Incharge", back_populates="user", uselist=False
    )
    teacher_assignments: Mapped[List["TeacherAssignment"]] = relationship(
        "TeacherAssignment", back_populates="teacher"
    )
    student_enrollments: Mapped[List["StudentEnrollment"]] = relationship(
        "StudentEnrollment",
        foreign_keys="StudentEnrollment.student_id",
        back_populates="student",
    )


class Incharge(Base):
    __tablename__ = "incharges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wing_name: Mapped[str] = mapped_column(String(100), default="General Wing")
    can_approve_teachers: Mapped[bool] = mapped_column(Boolean, default=True)
    can_approve_students: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    user: Mapped["User"] = relationship("User", back_populates="incharge_profile")


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 6 to 12
    section_name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "10-A"
    class_teacher_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    school: Mapped["School"] = relationship("School", back_populates="sections")
    teacher_assignments: Mapped[List["TeacherAssignment"]] = relationship(
        "TeacherAssignment", back_populates="section"
    )
    enrollments: Mapped[List["StudentEnrollment"]] = relationship(
        "StudentEnrollment", back_populates="section"
    )

    __table_args__ = (
        UniqueConstraint("school_id", "class_level", "section_name", name="uq_school_section"),
    )


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. MTH, PHY
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    school: Mapped["School"] = relationship("School", back_populates="subjects")
    teacher_assignments: Mapped[List["TeacherAssignment"]] = relationship(
        "TeacherAssignment", back_populates="subject"
    )

    __table_args__ = (
        UniqueConstraint("school_id", "code", name="uq_school_subject_code"),
    )


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    teacher: Mapped["User"] = relationship("User", back_populates="teacher_assignments")
    section: Mapped["Section"] = relationship("Section", back_populates="teacher_assignments")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="teacher_assignments")

    __table_args__ = (
        UniqueConstraint("teacher_id", "section_id", "subject_id", name="uq_teacher_section_subject"),
    )


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", index=True)
    approved_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], back_populates="student_enrollments"
    )
    section: Mapped["Section"] = relationship("Section", back_populates="enrollments")


# --- Library & RAG Tables ---
class FileRecord(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="PROCESSING", index=True)
    disclaimer_accepted: Mapped[bool] = mapped_column(Boolean, default=True)
    meta_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    chunks: Mapped[List["ChunkRecord"]] = relationship("ChunkRecord", back_populates="file")


class ChunkRecord(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    file_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    chapter: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(50), default="theory")  # theory, question, solution
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    file: Mapped["FileRecord"] = relationship("FileRecord", back_populates="chunks")


class SyllabusNode(Base):
    __tablename__ = "syllabus_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    board: Mapped[str] = mapped_column(String(50), index=True)  # ICSE, ISC, JEE, NEET
    class_level: Mapped[int] = mapped_column(Integer, index=True)
    subject_name: Mapped[str] = mapped_column(String(100), index=True)
    chapter: Mapped[str] = mapped_column(String(200), index=True)
    topic: Mapped[str] = mapped_column(String(200), index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)


# --- Questions & Verification ---
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    short_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    long_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    origin: Mapped[str] = mapped_column(String(50), nullable=False)
    source_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True
    )
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    versions: Mapped[List["QuestionVersion"]] = relationship(
        "QuestionVersion", back_populates="question"
    )


class QuestionVersion(Base):
    __tablename__ = "question_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    qid: Mapped[str] = mapped_column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", index=True)
    created_by_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    question: Mapped["Question"] = relationship("Question", back_populates="versions")
    verification_runs: Mapped[List["VerificationRun"]] = relationship(
        "VerificationRun", back_populates="question_version"
    )

    __table_args__ = (
        UniqueConstraint("qid", "version", name="uq_qid_version"),
    )


class VerificationRun(Base):
    __tablename__ = "verification_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    qid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    question_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("question_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_no: Mapped[int] = mapped_column(Integer, default=1)
    solver_model: Mapped[str] = mapped_column(String(100))
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    agree: Mapped[bool] = mapped_column(Boolean, default=False)
    diff_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    question_version: Mapped["QuestionVersion"] = relationship(
        "QuestionVersion", back_populates="verification_runs"
    )


# --- Papers, Tests, Proctoring & Analytics ---
class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    school_id: Mapped[str] = mapped_column(String(36), index=True)
    created_by_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    preset_type: Mapped[str] = mapped_column(String(50))  # Worksheet, Quiz, etc.
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    meta_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    items: Mapped[List["PaperItem"]] = relationship("PaperItem", back_populates="paper")


class PaperItem(Base):
    __tablename__ = "paper_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    paper_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    marks: Mapped[int] = mapped_column(Integer, default=1)
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)

    paper: Mapped["Paper"] = relationship("Paper", back_populates="items")


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    school_id: Mapped[str] = mapped_column(String(36), index=True)
    section_id: Mapped[str] = mapped_column(String(36), index=True)
    paper_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    created_by_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    proctoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    paper: Mapped["Paper"] = relationship("Paper")
    attempts: Mapped[List["Attempt"]] = relationship("Attempt", back_populates="test")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    test_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS", index=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    test: Mapped["Test"] = relationship("Test", back_populates="attempts")
    answers: Mapped[List["AttemptAnswer"]] = relationship("AttemptAnswer", back_populates="attempt")
    proctor_events: Mapped[List["ProctorEvent"]] = relationship(
        "ProctorEvent", back_populates="attempt"
    )


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    student_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    marks_awarded: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="answers")


class ProctorEvent(Base):
    __tablename__ = "proctor_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # TAB_SWITCH, BLUR, etc.
    event_meta_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="proctor_events")


# --- Organization: Bookmarks, Favourites, Collections, Notes ---
class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    __table_args__ = (UniqueConstraint("user_id", "qid", name="uq_user_bookmark"),)


class Favourite(Base):
    __tablename__ = "favourites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    __table_args__ = (UniqueConstraint("user_id", "qid", name="uq_user_favourite"),)


class QuestionNote(Base):
    __tablename__ = "question_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    collection_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    qid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- Analytics & Remedial ---
class TopicStat(Base):
    __tablename__ = "topic_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)  # student
    section_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)  # class level
    subject: Mapped[str] = mapped_column(String(100), index=True)
    chapter: Mapped[str] = mapped_column(String(200), index=True)
    topic: Mapped[str] = mapped_column(String(200), index=True)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )


class WeakTopic(Base):
    __tablename__ = "weak_topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    section_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    subject: Mapped[str] = mapped_column(String(100))
    chapter: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(String(200))
    severity: Mapped[str] = mapped_column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    identified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class RemedialPlan(Base):
    __tablename__ = "remedial_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    section_id: Mapped[str] = mapped_column(String(36), index=True)
    teacher_id: Mapped[str] = mapped_column(String(36), index=True)
    subject: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255))
    plan_json: Mapped[Any] = mapped_column(JSON)  # 5-day structured plan
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- System: Jobs, Audit, LLM Cache ---
class JobRecord(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class LLMCache(Base):
    __tablename__ = "llm_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    prompt_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
