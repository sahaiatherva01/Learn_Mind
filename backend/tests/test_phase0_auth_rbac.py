import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_phase0_flow(client: AsyncClient):
    # 1. Register School (Admin/Incharge creation)
    school_resp = await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "St. Xavier's Senior High School",
            "school_code": "STXAVIER",
            "board": "ICSE_ISC",
            "admin_name": "Father Francis (Incharge)",
            "admin_email": "incharge@stxaviers.edu",
            "admin_password": "securepassword123",
            "wing_name": "Senior Academic Wing",
        },
    )
    assert school_resp.status_code == 201
    school_data = school_resp.json()
    incharge_token = school_data["access_token"]
    incharge_headers = {"Authorization": f"Bearer {incharge_token}"}

    # 2. Incharge creates Sections and Subjects
    sec_resp = await client.post(
        "/api/v1/sections",
        json={"class_level": 10, "section_name": "10-A"},
        headers=incharge_headers,
    )
    assert sec_resp.status_code == 201
    sec_10a_id = sec_resp.json()["id"]

    sec_resp_12 = await client.post(
        "/api/v1/sections",
        json={"class_level": 12, "section_name": "12-PCM"},
        headers=incharge_headers,
    )
    assert sec_resp_12.status_code == 201

    # Create Subjects
    sub_math = await client.post(
        "/api/v1/subjects",
        json={"name": "Mathematics", "code": "MTH"},
        headers=incharge_headers,
    )
    assert sub_math.status_code == 201
    sub_math_id = sub_math.json()["id"]

    sub_phys = await client.post(
        "/api/v1/subjects",
        json={"name": "Physics", "code": "PHY"},
        headers=incharge_headers,
    )
    assert sub_phys.status_code == 201

    # 3. Register Teachers (Class Teacher & Subject Teacher)
    t1_resp = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "STXAVIER",
            "email": "sharma.maths@stxaviers.edu",
            "full_name": "Prof. R. D. Sharma",
            "password": "teacherpass123",
            "role": "CLASS_TEACHER",
        },
    )
    assert t1_resp.status_code == 201
    t1_id = t1_resp.json()["id"]
    assert t1_resp.json()["status"] == "PENDING_APPROVAL"

    t2_resp = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "STXAVIER",
            "email": "verma.physics@stxaviers.edu",
            "full_name": "Dr. H. C. Verma",
            "password": "teacherpass123",
            "role": "SUBJECT_TEACHER",
        },
    )
    assert t2_resp.status_code == 201
    t2_id = t2_resp.json()["id"]

    # 4. Incharge lists pending teachers and approves them
    pending_t_resp = await client.get(
        "/api/v1/incharge/teachers?status_filter=PENDING_APPROVAL",
        headers=incharge_headers,
    )
    assert pending_t_resp.status_code == 200
    assert len(pending_t_resp.json()) == 2

    # Incharge approves t1 as CLASS_TEACHER and t2 as SUBJECT_TEACHER
    appr_t1 = await client.post(
        f"/api/v1/incharge/teachers/{t1_id}/approve",
        json={"role": "CLASS_TEACHER"},
        headers=incharge_headers,
    )
    assert appr_t1.status_code == 200
    assert appr_t1.json()["status"] == "ACTIVE"

    appr_t2 = await client.post(
        f"/api/v1/incharge/teachers/{t2_id}/approve",
        json={"role": "SUBJECT_TEACHER"},
        headers=incharge_headers,
    )
    assert appr_t2.status_code == 200
    assert appr_t2.json()["status"] == "ACTIVE"

    # Assign t1 as Class Teacher for section 10-A
    assign_t1_math = await client.post(
        "/api/v1/sections/assign-teacher",
        json={
            "teacher_id": t1_id,
            "section_id": sec_10a_id,
            "subject_id": sub_math_id,
        },
        headers=incharge_headers,
    )
    assert assign_t1_math.status_code == 201

    # 5. Teacher Logins
    t1_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "sharma.maths@stxaviers.edu", "password": "teacherpass123"},
    )
    assert t1_login.status_code == 200
    t1_token = t1_login.json()["access_token"]
    t1_headers = {"Authorization": f"Bearer {t1_token}"}

    # Verify Teacher /auth/me returns assignments
    t1_me = await client.get("/api/v1/auth/me", headers=t1_headers)
    assert t1_me.status_code == 200
    assert len(t1_me.json()["assignments"]) == 1
    assert t1_me.json()["assignments"][0]["subject_code"] == "MTH"

    # 6. Student Registrations via all 3 supported methods
    # Method A: Email + school_code
    s1_resp = await client.post(
        "/api/v1/auth/register-student",
        json={
            "school_code": "STXAVIER",
            "email": "aarav.patel@student.stxaviers.edu",
            "full_name": "Aarav Patel",
            "password": "studentpassword123",
            "section_id": sec_10a_id,
        },
    )
    assert s1_resp.status_code == 201
    s1_token = s1_resp.json()["access_token"]
    s1_headers = {"Authorization": f"Bearer {s1_token}"}

    # Method B: Roll Number + school_code
    s2_resp = await client.post(
        "/api/v1/auth/register-student",
        json={
            "school_code": "STXAVIER",
            "roll_number": "ROLL-10A-042",
            "full_name": "Diya Sen",
            "password": "studentpassword123",
            "section_id": sec_10a_id,
        },
    )
    assert s2_resp.status_code == 201

    # Method C: Teacher-issued code
    s3_resp = await client.post(
        "/api/v1/auth/register-student",
        json={
            "school_code": "STXAVIER",
            "teacher_code": "TC-MATHS-991",
            "full_name": "Kabir Mehta",
            "password": "studentpassword123",
            "section_id": sec_10a_id,
        },
    )
    assert s3_resp.status_code == 201

    # 7. Test Login using Roll Number + School Code
    s2_login = await client.post(
        "/api/v1/auth/login",
        json={
            "roll_number": "ROLL-10A-042",
            "school_code": "STXAVIER",
            "password": "studentpassword123",
        },
    )
    assert s2_login.status_code == 200
    assert s2_login.json()["user"]["full_name"] == "Diya Sen"

    # Test Login using Teacher-issued Code
    s3_login = await client.post(
        "/api/v1/auth/login",
        json={
            "teacher_code": "TC-MATHS-991",
            "password": "studentpassword123",
        },
    )
    assert s3_login.status_code == 200
    assert s3_login.json()["user"]["full_name"] == "Kabir Mehta"

    # 8. Student section approval workflow
    # Incharge lists pending enrollments
    enr_list = await client.get("/api/v1/incharge/enrollments", headers=incharge_headers)
    assert enr_list.status_code == 200
    enrollments = enr_list.json()
    assert len(enrollments) == 3

    # Incharge approves s1 enrollment
    s1_enrollment_id = next(e["id"] for e in enrollments if e["student_name"] == "Aarav Patel")
    appr_enr_resp = await client.post(
        f"/api/v1/incharge/enrollments/{s1_enrollment_id}/approve",
        headers=incharge_headers,
    )
    assert appr_enr_resp.status_code == 200
    assert appr_enr_resp.json()["status"] == "APPROVED"

    # 9. Student Dashboard check
    s1_dash = await client.get("/api/v1/student/dashboard", headers=s1_headers)
    assert s1_dash.status_code == 200
    s1_dash_data = s1_dash.json()
    assert s1_dash_data["enrollment"]["status"] == "APPROVED"
    assert s1_dash_data["enrollment"]["section_name"] == "10-A"
    assert len(s1_dash_data["subjects"]) >= 1
    assert s1_dash_data["subjects"][0]["code"] == "MTH"

    # 10. Teacher Dashboard check
    t1_dash = await client.get("/api/v1/teacher/dashboard", headers=t1_headers)
    assert t1_dash.status_code == 200
    t1_dash_data = t1_dash.json()
    assert t1_dash_data["stats"]["assigned_classes_count"] == 1
    assert len(t1_dash_data["assignments"]) == 1

    # 11. Incharge Dashboard check
    incharge_dash = await client.get("/api/v1/incharge/dashboard", headers=incharge_headers)
    assert incharge_dash.status_code == 200
    assert incharge_dash.json()["stats"]["active_teachers"] == 2


@pytest.mark.asyncio
async def test_rbac_security_rules(client: AsyncClient):
    # Register a school and a student
    await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "Greenwood Academy",
            "school_code": "GREENWOOD",
            "board": "ICSE_ISC",
            "admin_name": "Admin Principal",
            "admin_email": "principal@greenwood.edu",
            "admin_password": "pass-greenwood-123",
        },
    )

    student_resp = await client.post(
        "/api/v1/auth/register-student",
        json={
            "school_code": "GREENWOOD",
            "email": "student1@greenwood.edu",
            "full_name": "Rohan Gupta",
            "password": "studentpass123",
        },
    )
    student_token = student_resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Rule E.1 Check: Student cannot access incharge or teacher routes (Default Deny / Forbidden)
    student_try_teachers = await client.get("/api/v1/incharge/teachers", headers=student_headers)
    assert student_try_teachers.status_code == 403

    student_try_sec_create = await client.post(
        "/api/v1/sections",
        json={"class_level": 9, "section_name": "9-B"},
        headers=student_headers,
    )
    assert student_try_sec_create.status_code == 403

    # Unauthenticated request to teacher dashboard
    unauth_resp = await client.get("/api/v1/teacher/dashboard")
    assert unauth_resp.status_code == 401
