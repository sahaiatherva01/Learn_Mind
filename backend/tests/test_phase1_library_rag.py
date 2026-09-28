import pytest
from httpx import AsyncClient


def create_test_pdf_bytes(title: str = "Class 12 Mathematics - Integral Calculus") -> bytes:
    """
    Generates a valid, multi-page test PDF containing chapters, theory, and questions.
    """
    # A standard raw PDF text stream:
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 7 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 7 0 R >> >> >>\nendobj\n"
        b"5 0 obj\n<< /Length 195 >>\nstream\n"
        b"BT\n/F1 12 Tf\n50 700 Td\n(Chapter: Calculus - Integral) Tj\n0 -25 Td\n(Topic: Indefinite Integrals and Substitution) Tj\n0 -30 Td\n(Integration is the reverse process of differentiation.) Tj\n0 -30 Td\n(Question 1. Evaluate the integral of x * exp(x) dx using integration by parts.) Tj\nET\n"
        b"endstream\nendobj\n"
        b"6 0 obj\n<< /Length 180 >>\nstream\n"
        b"BT\n/F1 12 Tf\n50 700 Td\n(Chapter: Electrostatics) Tj\n0 -25 Td\n(Topic: Coulomb's Law and Electric Field) Tj\n0 -30 Td\n(The electric force between two point charges is inversely proportional to square of distance.) Tj\n0 -30 Td\n(Question 2. Find the electric field due to a point charge Q at distance r.) Tj\nET\n"
        b"endstream\nendobj\n"
        b"7 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 8\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000223 00000 n \n0000000331 00000 n \n0000000577 00000 n \n0000000808 00000 n \n"
        b"trailer\n<< /Size 8 /Root 1 0 R >>\nstartxref\n875\n%%EOF\n"
    )
    return pdf_content


@pytest.mark.asyncio
async def test_phase1_library_upload_chunking_and_search(client: AsyncClient):
    # 1. Register School & Teacher
    school_resp = await client.post(
        "/api/v1/auth/register-school",
        json={
            "school_name": "Cambridge School",
            "school_code": "CAMBRIDGE",
            "board": "ISC",
            "admin_name": "Head Incharge",
            "admin_email": "incharge@cambridge.edu",
            "admin_password": "pass123456",
        },
    )
    incharge_token = school_resp.json()["access_token"]
    incharge_headers = {"Authorization": f"Bearer {incharge_token}"}

    # Register Teacher 1
    t1_reg = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "CAMBRIDGE",
            "email": "ramanujan.math@cambridge.edu",
            "full_name": "Srinivasa Ramanujan",
            "password": "teacherpass123",
            "role": "SUBJECT_TEACHER",
        },
    )
    t1_id = t1_reg.json()["id"]

    # Register Teacher 2 (to test private library isolation per Rules.md A.3)
    t2_reg = await client.post(
        "/api/v1/auth/register-teacher",
        json={
            "school_code": "CAMBRIDGE",
            "email": "einstein.phys@cambridge.edu",
            "full_name": "Albert Einstein",
            "password": "teacherpass123",
            "role": "SUBJECT_TEACHER",
        },
    )
    t2_id = t2_reg.json()["id"]

    # Approve both teachers
    await client.post(f"/api/v1/incharge/teachers/{t1_id}/approve", headers=incharge_headers)
    await client.post(f"/api/v1/incharge/teachers/{t2_id}/approve", headers=incharge_headers)

    # Log in as Teacher 1
    t1_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "ramanujan.math@cambridge.edu", "password": "teacherpass123"},
    )
    t1_headers = {"Authorization": f"Bearer {t1_login.json()['access_token']}"}

    # Log in as Teacher 2
    t2_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "einstein.phys@cambridge.edu", "password": "teacherpass123"},
    )
    t2_headers = {"Authorization": f"Bearer {t2_login.json()['access_token']}"}

    # 2. Test Syllabus Tree API
    syl_resp = await client.get("/api/v1/library/syllabus?board=ISC", headers=t1_headers)
    assert syl_resp.status_code == 200
    syl_data = syl_resp.json()
    assert syl_data["total_nodes"] > 0
    assert "ISC" in syl_data["tree"]

    # 3. Teacher 1 Uploads PDF without disclaimer -> Fails (Rules.md D.8)
    pdf_bytes = create_test_pdf_bytes("Calculus Vol 1")
    upload_no_disc = await client.post(
        "/api/v1/library/upload",
        files={"file": ("calculus_vol1.pdf", pdf_bytes, "application/pdf")},
        data={"disclaimer_accepted": "false"},
        headers=t1_headers,
    )
    assert upload_no_disc.status_code == 422

    # Teacher 1 Uploads with disclaimer accepted
    upload_resp = await client.post(
        "/api/v1/library/upload",
        files={"file": ("calculus_vol1.pdf", pdf_bytes, "application/pdf")},
        data={"disclaimer_accepted": "true"},
        headers=t1_headers,
    )
    assert upload_resp.status_code == 201
    file_data = upload_resp.json()
    file_id = file_data["id"]
    assert file_data["filename"] == "calculus_vol1.pdf"

    # 4. Check File Details and Chunk breakdown
    file_det_resp = await client.get(f"/api/v1/library/files/{file_id}", headers=t1_headers)
    assert file_det_resp.status_code == 200
    file_det = file_det_resp.json()
    assert file_det["status"] in ["READY", "PROCESSING"]
    assert file_det["total_chunks"] >= 2

    # 5. Hybrid Search inside Teacher 1's files
    search_resp = await client.get(
        "/api/v1/library/search?query=Evaluate+the+integral+using+parts",
        headers=t1_headers,
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["results_count"] > 0
    top_hit = search_data["results"][0]
    assert "integral" in top_hit["content"].lower()
    assert "Book: calculus_vol1.pdf" in top_hit["source_label"]
    assert top_hit["chapter"] is not None

    # 6. Rule A.3 Isolation Check: Teacher 2 cannot search or see Teacher 1's uploaded files
    t2_files_resp = await client.get("/api/v1/library/files", headers=t2_headers)
    assert t2_files_resp.status_code == 200
    assert len(t2_files_resp.json()) == 0  # Teacher 2 has 0 files

    # Teacher 2 searching for Teacher 1's book content returns 0 results
    t2_search = await client.get(
        "/api/v1/library/search?query=Evaluate+the+integral",
        headers=t2_headers,
    )
    assert t2_search.status_code == 200
    assert t2_search.json()["results_count"] == 0

    # Teacher 2 trying to access Teacher 1's file directly returns 404 (Not Found in their library)
    t2_get_file = await client.get(f"/api/v1/library/files/{file_id}", headers=t2_headers)
    assert t2_get_file.status_code == 404
