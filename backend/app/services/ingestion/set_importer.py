# Question Set Importer (G2 Graph) per Rules.md C.8 & ARCH.md §4
import json
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import llm_client
from app.services.generation.prompts import prompt_manager
from app.services.generation.studio import question_studio_service
from app.services.verification.verifier import solve_twice_verifier


class QuestionSetImporterService:
    """
    G2 Question-set interpretation pipeline:
    Extract questions -> Classify -> Build interpretation summary -> WAIT for teacher confirm -> Import to bank.
    Rules.md C.8: Uploaded question sets require a teacher confirmation step before import.
    """

    async def parse_and_interpret_set(
        self,
        raw_text: str,
        board: str = "ICSE",
        class_level: int = 12,
        subject: str = "Mathematics",
    ) -> dict[str, Any]:
        """
        Step 1: Extract questions and produce Interpretation Summary for teacher confirmation.
        """
        prompt = prompt_manager.render(
            subject_dir="general",
            prompt_type="interpret",
            raw_text=raw_text,
            board=board,
            class_level=class_level,
            subject=subject,
        )

        response = await llm_client.generate(
            prompt=prompt,
            model_tier="strong",
            temperature=0.2,
        )
        text_output = response.get("text", "")

        interpretation_summary = f"Detected question set for {subject} Class {class_level} ({board})."
        parsed_questions = []

        try:
            match = re.search(r"\{.*\}", text_output, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                interpretation_summary = data.get("interpretation_summary", interpretation_summary)
                parsed_questions = data.get("questions", [])
        except Exception:
            pass

        if not parsed_questions:
            # Fallback heuristic question splitter if LLM returns unstructured text
            blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
            for idx, block in enumerate(blocks, 1):
                parsed_questions.append({
                    "body": block,
                    "options": None,
                    "answer": "Pending teacher verification",
                    "solution": None,
                    "question_type": "SHORT_ANSWER",
                    "chapter": "Imported Set",
                    "topic": "General",
                    "difficulty": "MEDIUM",
                    "marks": 2,
                })
            interpretation_summary = f"Heuristically extracted {len(parsed_questions)} questions. Please review before confirmation."

        return {
            "interpretation_summary": interpretation_summary,
            "detected_subject": subject,
            "detected_class": class_level,
            "questions_count": len(parsed_questions),
            "questions": parsed_questions,
        }

    async def confirm_and_import_set(
        self,
        db: AsyncSession,
        teacher_id: str,
        school_id: str,
        confirmed_questions: list[dict[str, Any]],
        source_ref: str | None = "Imported Question Set",
    ) -> list[dict[str, Any]]:
        """
        Step 2: Teacher confirms interpretation -> Import to Question Bank with Solve-Twice verification.
        """
        imported_results = []

        for item in confirmed_questions:
            subject = item.get("subject", "Mathematics")
            class_level = int(item.get("class_level", 12))
            chapter = item.get("chapter", "Calculus")
            topic = item.get("topic", "General")
            body = item.get("body", "")
            options = item.get("options")
            answer = item.get("answer", "A")
            solution = item.get("solution")
            marks = int(item.get("marks", 1))
            difficulty = item.get("difficulty", "MEDIUM")
            q_type = item.get("question_type", "MCQ")

            # Run Solve-Twice Verification
            verification = await solve_twice_verifier.verify_question(
                subject=subject,
                question_type=q_type,
                body=body,
                options=options,
                draft_answer=answer,
                draft_solution=solution,
            )

            draft_payload = {
                "subject": subject,
                "class_level": class_level,
                "chapter": chapter,
                "topic": topic,
                "question_type": q_type,
                "difficulty": difficulty,
                "marks": marks,
                "mode": "SOURCE_COPY",
                "source_ref": source_ref,
                "draft": {
                    "body": body,
                    "options": options,
                    "answer": answer,
                    "solution": solution,
                },
                "verification": {
                    "agree": verification.agree,
                    "status": verification.status,
                    "diff_notes": verification.diff_notes,
                    "solver1": {
                        "model": verification.solver1.model,
                        "answer": verification.solver1.answer,
                        "steps": verification.solver1.steps,
                    },
                    "solver2": {
                        "model": verification.solver2.model,
                        "answer": verification.solver2.answer,
                        "steps": verification.solver2.steps,
                    },
                },
            }

            saved = await question_studio_service.save_draft_to_bank(
                db=db,
                teacher_id=teacher_id,
                school_id=school_id,
                draft_payload=draft_payload,
                approve=False,  # Teacher explicitly approves later per Rules.md C.2
            )
            imported_results.append(saved)

        return imported_results


question_set_importer = QuestionSetImporterService()
