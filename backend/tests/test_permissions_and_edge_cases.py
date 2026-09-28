import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_school_approval_and_dashboard(client: AsyncClient):
    # Register school 1
    s1_resp = await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "Delhi Public School",
            "school_code": "DPS001",
            "board": "ICSE_ISC",
            "admin_name": "Incharge DPS",
            "admin_email": "incharge@dps.edu",
            "admin_password": "password123",
        },
    )
    assert s1_resp.status_code == 201

    # Attempt to register duplicate school code
    dup_resp = await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "Duplicate School",
            "school_code": "DPS001",
            "board": "ICSE_ISC",
            "admin_name": "Admin 2",
            "admin_email": "admin2@dps.edu",
            "admin_password": "password123",
        },
    )
    assert dup_resp.status_code == 409
    assert dup_resp.json()["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_class_teacher_vs_subject_teacher_permissions(client: AsyncClient):
    # Register School
    school_resp = await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "Loyola High",
            "school_code": "LOYOLA",
            "board": "ICSE_ISC",
            "admin_name": "Fr. Principal",
            "admin_email": "incharge@loyola.edu",
            "admin_password": "loyolapassword123",
        },
    )
    incharge_token = school_resp.json()["access_token"]
    incharge_headers = {"Authorization": f"Bearer {incharge_token}"}

    # Incharge creates section
    sec_resp = await client.post(
        "/api/v1/sections",
        json={"class_level": 11, "section_name": "11-A"},
        headers=incharge_headers,
    )
    sec_id = sec_resp.json()["id"]

    # Incharge creates subject
    subj_resp = await client.post(
        "/api/v1/subjects",
        json={"name": "Chemistry", "code": "CHE"},
        headers=incharge_headers,
    )
    subj_id = subj_resp.json()["id"]

    # Register Teacher 1 (Class Teacher)
    t1_resp = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "LOYOLA",
            "email": "classteacher@loyola.edu",
            "full_name": "Teacher Alpha",
            "password": "teacherpass123",
            "role": "CLASS_TEACHER",
        },
    )
    t1_id = t1_resp.json()["id"]

    # Register Teacher 2 (Subject Teacher)
    t2_resp = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "LOYOLA",
            "email": "subjectteacher@loyola.edu",
            "full_name": "Teacher Beta",
            "password": "teacherpass123",
            "role": "SUBJECT_TEACHER",
        },
    )
    t2_id = t2_resp.json()["id"]

    # Incharge approves both
    await client.post(f"/api/v1/incharge/teachers/{t1_id}/approve", headers=incharge_headers)
    await client.post(f"/api/v1/incharge/teachers/{t2_id}/approve", headers=incharge_headers)

    # Assign Teacher Alpha as Class Teacher for 11-A
    await client.post(
        "/api/v1/sections/assign-teacher",
        json={"teacher_id": t1_id, "section_id": sec_id, "subject_id": subj_id},
        headers=incharge_headers,
    )

    # Register Student
    student_resp = await client.post(
        "/api/v1/auth/register-student",
        json={
            "school_code": "LOYOLA",
            "email": "student@loyola.edu",
            "full_name": "Tanmay Roy",
            "password": "studentpass123",
            "section_id": sec_id,
        },
    )
    student_token = student_resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Subject Teacher Login
    t2_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "subjectteacher@loyola.edu", "password": "teacherpass123"},
    )
    t2_headers = {"Authorization": f"Bearer {t2_login.json()['access_token']}"}

    # Subject Teacher tries to access enrollment approval list -> Forbidden (Rules.md A.7)
    t2_try_enr = await client.get("/api/v1/teacher/enrollments", headers=t2_headers)
    assert t2_try_enr.status_code == 403

    # Student tries to access teacher roster -> Forbidden
    s_try_roster = await client.get("/api/v1/teacher/students", headers=student_headers)
    assert s_try_roster.status_code == 403
