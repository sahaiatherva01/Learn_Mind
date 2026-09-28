import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.db.models import School, User
from app.services.questions.id_generator import question_id_service
from app.services.verification.verifier import solve_twice_verifier


@pytest.mark.asyncio
async def test_question_id_generation_and_query_parsing(db_session: AsyncSession):
    # Test Short ID format
    short_id = await question_id_service.generate_unique_short_id(db_session)
    assert short_id.startswith("Q-")
    assert len(short_id) == 8  # "Q-" + 6 base32 chars
    # Ensure no confusing chars (0, 1, I, L, O)
    assert not any(c in short_id[2:] for c in "01ILO")

    # Test Long ID format
    long_id = await question_id_service.generate_long_id(
        db=db_session,
        subject="Mathematics",
        class_level=12,
        chapter="Calculus",
        topic="Definite Integrals",
    )
    assert long_id.startswith("MTH-12-CAL-DEF-000001")

    # Test Query Parsing
    parsed_short = question_id_service.parse_query("Q-8K3F2A")
    assert parsed_short.query_type == "SHORT_ID"
    assert parsed_short.short_id == "Q-8K3F2A"

    parsed_ver = question_id_service.parse_query("Q-8K3F2A@v2")
    assert parsed_ver.query_type == "SHORT_ID_VERSION"
    assert parsed_ver.short_id == "Q-8K3F2A"
    assert parsed_ver.version == 2

    parsed_long = question_id_service.parse_query("MTH-12-CAL-DEF-000001")
    assert parsed_long.query_type == "LONG_ID"
    assert parsed_long.long_id == "MTH-12-CAL-DEF-000001"

    parsed_text = question_id_service.parse_query("evaluate integral of sin(x)")
    assert parsed_text.query_type == "TEXT"
    assert parsed_text.text_query == "evaluate integral of sin(x)"


@pytest.mark.asyncio
async def test_solve_twice_verifier_tools():
    # 1. SymPy symbolic equivalence
    eq1 = "x**2 + 2*x + 1"
    eq2 = "(x + 1)**2"
    assert solve_twice_verifier.compare_sympy_expressions(eq1, eq2) is True

    # 2. Numerical tolerance
    assert solve_twice_verifier.compare_numerical("42.005", "42.001", tolerance=0.01) is True
    assert solve_twice_verifier.compare_numerical("42.5", "40.0", tolerance=0.01) is False

    # 3. Python code sandbox execution
    py_code = "a = 5\nb = 10\nprint(f'Sum: {a+b}')"
    out = solve_twice_verifier.execute_python_code_sandbox(py_code)
    assert out == "Sum: 15"

    # 4. Sandbox blocks unsafe imports
    unsafe_code = "import os\nos.system('ls')"
    unsafe_out = solve_twice_verifier.execute_python_code_sandbox(unsafe_code)
    assert "Disallowed import" in unsafe_out


@pytest.mark.asyncio
async def test_question_studio_and_bank_endpoints(client: AsyncClient, db_session: AsyncSession):
    # Setup test School and Users (Teacher and Student)
    school = School(name="St. Xavier's High School", code="STX123", status="APPROVED")
    db_session.add(school)
    await db_session.flush()

    teacher = User(
        school_id=school.id,
        email="teacher_q@test.com",
        full_name="Prof. Sharma",
        role="SUBJECT_TEACHER",
        password_hash=get_password_hash("teacher123"),
        status="ACTIVE",
    )
    student = User(
        school_id=school.id,
        email="student_q@test.com",
        full_name="Rahul Verma",
        role="STUDENT",
        roll_number="STX-2026-001",
        password_hash=get_password_hash("student123"),
        status="ACTIVE",
    )
    db_session.add_all([teacher, student])
    await db_session.commit()

    teacher_token = create_access_token(subject=teacher.id, role=teacher.role, school_id=school.id)
    student_token = create_access_token(subject=student.id, role=student.role, school_id=school.id)

    # 1. Test Studio Generation endpoint (G3 Graph)
    gen_payload = {
        "subject": "Mathematics",
        "class_level": 12,
        "chapter": "Calculus",
        "topic": "Definite Integrals",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "marks": 1,
        "mode": "AI_SIMILAR",
    }
    gen_res = await client.post(
        "/api/v1/studio/generate",
        json=gen_payload,
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert gen_res.status_code == 200
    draft_data = gen_res.json()
    assert "draft" in draft_data
    assert "verification" in draft_data
    assert draft_data["verification"]["solver1"]["answer"] is not None
    assert draft_data["verification"]["solver2"]["answer"] is not None

    # 2. Save Draft to Question Bank
    save_payload = {
        "subject": "Mathematics",
        "class_level": 12,
        "chapter": "Calculus",
        "topic": "Definite Integrals",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "marks": 1,
        "mode": "AI_SIMILAR",
        "source_ref": "Page 142 (ISC Mathematics Vol 2)",
        "draft": {
            "body": "Evaluate $\\int_{0}^{\\pi/2} \\sin^2(x) dx$",
            "options": ["A) $\\pi/4$", "B) $\\pi/2$", "C) $1$", "D) $0$"],
            "answer": "A",
            "solution": "Use Walli's formula: $\\int_{0}^{\\pi/2} \\sin^2(x) dx = \\frac{1}{2} \\cdot \\frac{\\pi}{2} = \\frac{\\pi}{4}$",
        },
        "verification": draft_data["verification"],
        "approve": False,
    }
    save_res = await client.post(
        "/api/v1/studio/save-draft",
        json=save_payload,
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert save_res.status_code == 201
    saved_q = save_res.json()
    qid = saved_q["id"]
    short_id = saved_q["short_id"]
    assert saved_q["status"] == "UNVERIFIED"

    # 3. Test Versioning (Edit question to create v2 per Rules.md B.2)
    edit_payload = {
        "body": "Evaluate $\\int_{0}^{\\pi/2} \\sin^2(x) dx$ with limits clarified",
        "options": ["A) $\\pi/4$", "B) $\\pi/2$", "C) $1$", "D) $0$"],
        "answer": "A",
        "solution": "Step 1: Use property $\\int_0^a f(x)dx = \\int_0^a f(a-x)dx$.\nStep 2: $2I = \\pi/2 \\implies I = \\pi/4$",
        "verification_status": "UNVERIFIED",
    }
    edit_res = await client.post(
        f"/api/v1/questions/{qid}/versions",
        json=edit_payload,
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert edit_res.status_code == 201
    assert edit_res.json()["version"] == 2

    # 4. Search Question by Short ID and Short ID with version
    search_short = await client.get(
        f"/api/v1/questions/search?q={short_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert search_short.status_code == 200
    assert search_short.json()["total"] == 1

    search_v1 = await client.get(
        f"/api/v1/questions/search?q={short_id}@v1",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert search_v1.status_code == 200
    assert search_v1.json()["questions"][0]["version_data"]["version"] == 1

    # 5. Approve Question Version v2
    approve_res = await client.patch(
        f"/api/v1/questions/{qid}/versions/2/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["verification_status"] == "APPROVED"

    # 6. Verify Student Access & Field-Level Redaction (Rules.md A.4 & A.5)
    # Student views approved question
    student_get = await client.get(
        f"/api/v1/questions/{qid}?v=2",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert student_get.status_code == 200
    student_data = student_get.json()
    # Source ref MUST be None for student
    assert student_data["source_ref"] is None
    # Solution steps MUST be None for student
    assert student_data["version_data"]["solution"] is None
    # Verification runs MUST be empty for student
    assert student_data["version_data"]["verification_runs"] == []
    # Answer key IS visible
    assert student_data["version_data"]["answer"] == "A"


@pytest.mark.asyncio
async def test_question_set_import_with_interpretation_confirmation(client: AsyncClient, db_session: AsyncSession):
    # Setup test teacher
    school = School(name="Bishop Cotton Boys", code="BCB456", status="APPROVED")
    db_session.add(school)
    await db_session.flush()

    teacher = User(
        school_id=school.id,
        email="teacher_import@test.com",
        full_name="Prof. Rao",
        role="SUBJECT_TEACHER",
        password_hash=get_password_hash("teacher123"),
        status="ACTIVE",
    )
    db_session.add(teacher)
    await db_session.commit()
    teacher_token = create_access_token(subject=teacher.id, role=teacher.role, school_id=school.id)

    # Step 1: Interpret unformatted test paper
    raw_text = """
    Q1. Find the derivative of f(x) = x^3 - 3x + 2 at x=2.
    Options: A) 9, B) 12, C) 6, D) 3
    Answer: A

    Q2. Solve the differential equation dy/dx = 2x.
    Answer: y = x^2 + C
    """
    interpret_res = await client.post(
        "/api/v1/studio/interpret-set",
        json={
            "raw_text": raw_text,
            "board": "ISC",
            "class_level": 12,
            "subject": "Mathematics",
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert interpret_res.status_code == 200
    data = interpret_res.json()
    assert "interpretation_summary" in data
    assert data["questions_count"] >= 1

    # Step 2: Teacher confirms interpretation -> Import to bank
    confirm_res = await client.post(
        "/api/v1/studio/confirm-import-set",
        json={
            "questions": data["questions"],
            "source_ref": "Uploaded Prelim Paper 2026",
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert confirm_res.status_code == 201
    confirm_data = confirm_res.json()
    assert confirm_data["imported_count"] >= 1
    assert confirm_data["questions"][0]["short_id"].startswith("Q-")
