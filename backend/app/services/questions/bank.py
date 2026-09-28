# Question Bank, Versioning, Deduplication & Collections Service
import hashlib
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Question,
    QuestionVersion,
    VerificationRun,
)
from app.services.questions.id_generator import question_id_service


class QuestionBankService:
    """
    Core Question Bank Service.
    Rules.md B.1-B.7: Immutable IDs, explicit versions, deduplication, metadata.
    Rules.md A.4-A.5: Source citation and solution step redaction for student payloads.
    """

    @staticmethod
    def compute_text_hash(text: str) -> str:
        # Normalize whitespace and lowercase
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    async def check_duplicate(
        self,
        db: AsyncSession,
        body_text: str,
        school_id: str,
    ) -> bool:
        """
        Duplicate detection via normalized text hash against existing questions.
        Rules.md B.7: Duplicate detection before saving to bank.
        """
        target_hash = self.compute_text_hash(body_text)
        stmt = (
            select(QuestionVersion.body)
            .join(Question, Question.id == QuestionVersion.qid)
            .where(Question.school_id == school_id)
        )
        result = await db.execute(stmt)
        existing_bodies = result.scalars().all()

        for eb in existing_bodies:
            if self.compute_text_hash(eb) == target_hash:
                return True
        return False

    async def create_question(
        self,
        db: AsyncSession,
        teacher_id: str,
        school_id: str,
        subject: str,
        class_level: int,
        chapter: str,
        topic: str,
        origin: str,  # SOURCE_COPY | AI_SIMILAR | AI_HIGHER | TEACHER_AUTHORED
        body: str,
        options: list[str] | None,
        answer: str,
        solution: str | None,
        marks: int = 1,
        difficulty: str = "MEDIUM",
        question_type: str = "MCQ",
        source_ref: str | None = None,
        verification_status: str = "UNVERIFIED",
        meta_json: dict[str, Any] | None = None,
    ) -> Question:
        """
        Creates a new immutable Question with Short ID, Long ID, and Version 1.
        """
        short_id = await question_id_service.generate_unique_short_id(db)
        long_id = await question_id_service.generate_long_id(
            db=db,
            subject=subject,
            class_level=class_level,
            chapter=chapter,
            topic=topic,
        )

        merged_meta = meta_json or {}
        merged_meta.update({
            "subject": subject,
            "class_level": class_level,
            "chapter": chapter,
            "topic": topic,
            "marks": marks,
            "difficulty": difficulty,
            "question_type": question_type,
        })

        new_q = Question(
            short_id=short_id,
            long_id=long_id,
            origin=origin,
            source_ref=source_ref,
            owner_teacher_id=teacher_id,
            school_id=school_id,
            current_version=1,
        )
        db.add(new_q)
        await db.flush()

        v1 = QuestionVersion(
            qid=new_q.id,
            version=1,
            body=body,
            options_json=options,
            answer=answer,
            solution=solution,
            meta_json=merged_meta,
            verification_status=verification_status,
            created_by_id=teacher_id,
        )
        db.add(v1)
        await db.flush()

        return new_q

    async def create_new_version(
        self,
        db: AsyncSession,
        qid: str,
        user_id: str,
        body: str,
        options: list[str] | None,
        answer: str,
        solution: str | None,
        verification_status: str = "UNVERIFIED",
        meta_json: dict[str, Any] | None = None,
    ) -> QuestionVersion:
        """
        Edits create a new version under the same QID.
        Rules.md B.2: Never fork silently.
        """
        q_stmt = select(Question).where(Question.id == qid)
        res = await db.execute(q_stmt)
        question = res.scalar_one_or_none()
        if not question:
            raise ValueError(f"Question {qid} not found")

        next_version = question.current_version + 1
        question.current_version = next_version

        # Merge previous meta if not provided
        if meta_json is None:
            prev_v_stmt = select(QuestionVersion).where(
                and_(QuestionVersion.qid == qid, QuestionVersion.version == next_version - 1)
            )
            prev_res = await db.execute(prev_v_stmt)
            prev_v = prev_res.scalar_one_or_none()
            meta_json = prev_v.meta_json if prev_v else {}

        new_v = QuestionVersion(
            qid=qid,
            version=next_version,
            body=body,
            options_json=options,
            answer=answer,
            solution=solution,
            meta_json=meta_json,
            verification_status=verification_status,
            created_by_id=user_id,
        )
        db.add(new_v)
        await db.flush()
        return new_v

    async def record_verification_runs(
        self,
        db: AsyncSession,
        qid: str,
        version: int,
        version_id: str,
        solver1_ans: str,
        solver1_steps: str,
        solver1_model: str,
        solver2_ans: str,
        solver2_steps: str,
        solver2_model: str,
        agree: bool,
        diff_notes: str | None = None,
    ) -> None:
        """
        Stores individual solver verification runs for full auditability.
        """
        run1 = VerificationRun(
            qid=qid,
            version=version,
            question_version_id=version_id,
            run_no=1,
            solver_model=solver1_model,
            answer=solver1_ans,
            steps=solver1_steps,
            agree=agree,
            diff_notes=diff_notes,
        )
        run2 = VerificationRun(
            qid=qid,
            version=version,
            question_version_id=version_id,
            run_no=2,
            solver_model=solver2_model,
            answer=solver2_ans,
            steps=solver2_steps,
            agree=agree,
            diff_notes=diff_notes,
        )
        db.add_all([run1, run2])
        await db.flush()

    async def search_questions(
        self,
        db: AsyncSession,
        school_id: str,
        raw_query: str | None = None,
        subject: str | None = None,
        class_level: int | None = None,
        chapter: str | None = None,
        status: str | None = None,
        origin: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Searches questions with multi-modal ID parser (Short ID, Short@vN, Long ID, text).
        """
        stmt = (
            select(Question)
            .options(
                selectinload(Question.versions).selectinload(QuestionVersion.verification_runs)
            )
            .where(Question.school_id == school_id)
        )

        target_version: int | None = None

        if raw_query and raw_query.strip():
            parsed = question_id_service.parse_query(raw_query)
            if parsed.query_type == "SHORT_ID":
                stmt = stmt.where(Question.short_id == parsed.short_id)
            elif parsed.query_type == "SHORT_ID_VERSION":
                stmt = stmt.where(Question.short_id == parsed.short_id)
                target_version = parsed.version
            elif parsed.query_type == "LONG_ID":
                stmt = stmt.where(Question.long_id == parsed.long_id)
            elif parsed.query_type == "TEXT" and parsed.text_query:
                # Text search on question body
                stmt = stmt.join(QuestionVersion, QuestionVersion.qid == Question.id).where(
                    QuestionVersion.body.ilike(f"%{parsed.text_query}%")
                )

        if origin:
            stmt = stmt.where(Question.origin == origin)

        stmt = stmt.order_by(desc(Question.created_at)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        questions = result.scalars().unique().all()

        formatted = []
        for q in questions:
            # Pick active version
            chosen_v = None
            if target_version is not None:
                for v in q.versions:
                    if v.version == target_version:
                        chosen_v = v
                        break
            if chosen_v is None:
                for v in q.versions:
                    if v.version == q.current_version:
                        chosen_v = v
                        break
            if chosen_v is None and q.versions:
                chosen_v = q.versions[0]

            if not chosen_v:
                continue

            meta = chosen_v.meta_json or {}

            # Filter by subject, class, chapter, status if specified
            if subject and meta.get("subject", "").lower() != subject.lower():
                continue
            if class_level and meta.get("class_level") != class_level:
                continue
            if chapter and chapter.lower() not in meta.get("chapter", "").lower():
                continue
            if status and chosen_v.verification_status != status:
                continue

            runs = [
                {
                    "run_no": r.run_no,
                    "solver_model": r.solver_model,
                    "answer": r.answer,
                    "steps": r.steps,
                    "agree": r.agree,
                    "diff_notes": r.diff_notes,
                }
                for r in (chosen_v.verification_runs or [])
            ]

            formatted.append({
                "id": q.id,
                "short_id": q.short_id,
                "long_id": q.long_id,
                "origin": q.origin,
                "source_ref": q.source_ref,
                "owner_teacher_id": q.owner_teacher_id,
                "current_version": q.current_version,
                "version_data": {
                    "id": chosen_v.id,
                    "version": chosen_v.version,
                    "body": chosen_v.body,
                    "options": chosen_v.options_json,
                    "answer": chosen_v.answer,
                    "solution": chosen_v.solution,
                    "verification_status": chosen_v.verification_status,
                    "meta": meta,
                    "verification_runs": runs,
                },
                "created_at": q.created_at.isoformat(),
            })

        return formatted

    @staticmethod
    def sanitize_for_student(question_data: dict[str, Any]) -> dict[str, Any]:
        """
        Enforces Rules.md A.4 & A.5:
        - Source citation is REDACTED.
        - Solution steps, derivation, verification runs, and solver notes are REDACTED.
        - Students receive ONLY the question body, options, and final answer key (if permitted).
        """
        sanitized = dict(question_data)
        sanitized["source_ref"] = None
        if "version_data" in sanitized:
            v = dict(sanitized["version_data"])
            v["solution"] = None
            v["verification_runs"] = []
            sanitized["version_data"] = v
        return sanitized


question_bank_service = QuestionBankService()
