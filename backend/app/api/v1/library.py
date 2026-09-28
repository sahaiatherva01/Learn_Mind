import os
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_teacher
from app.core.errors import (
    NotFoundError,
    ValidationError,
)
from app.core.logging import logger
from app.db.models import ChunkRecord, FileRecord, User
from app.db.session import get_db
from app.services.ingestion.parser import pdf_parser
from app.services.ingestion.pipeline import ingestion_pipeline
from app.services.ingestion.syllabus import syllabus_service
from app.services.retrieval.search import hybrid_search

router = APIRouter(prefix="/library", tags=["Library & RAG"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_library_file(
    file: UploadFile = File(...),
    disclaimer_accepted: str = Form("true"),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Rule D.8: Copyright disclaimer acceptance
    is_accepted = str(disclaimer_accepted).strip().lower() in ["true", "1", "yes"]
    if not is_accepted:
        raise ValidationError(
            "You must accept the copyright disclaimer confirming you have the right to use this material for teaching"
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are supported in V1")

    # Read bytes
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File size exceeds limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB"
        )

    if not pdf_parser.validate_pdf_bytes(content):
        raise ValidationError("Invalid or corrupted PDF file header")

    # Save to disk
    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(content)

    file_record = FileRecord(
        id=file_id,
        teacher_id=current_user.id,
        school_id=current_user.school_id or "default",
        filename=file.filename,
        file_path=str(save_path),
        file_size=len(content),
        status="PROCESSING",
        disclaimer_accepted=True,
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)

    # Process ingestion pipeline (parse -> chunk -> embed -> tag)
    try:
        res = await ingestion_pipeline.process_file(db, file_id, content)
        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "file_size": file_record.file_size,
            "status": "READY",
            "chunks_count": res["chunks_count"],
            "chapters": res["chapters"],
            "topics": res["topics"],
            "message": "File parsed, chunked, and tagged with syllabus chapters.",
        }
    except Exception as e:
        logger.error(f"Ingestion error for {file_id}: {e}")
        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "file_size": file_record.file_size,
            "status": "PROCESSING",
            "message": "File uploaded and queued for processing.",
        }


@router.get("/files")
async def list_teacher_files(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Rule A.3: Private by default: teacher's uploads visible ONLY to that teacher
    stmt = (
        select(FileRecord)
        .where(FileRecord.teacher_id == current_user.id)
        .order_by(FileRecord.created_at.desc())
    )
    res = await db.execute(stmt)
    files = res.scalars().all()

    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_size": f.file_size,
            "status": f.status,
            "metadata": f.meta_json,
            "created_at": f.created_at,
        }
        for f in files
    ]


@router.get("/files/{file_id}")
async def get_file_details(
    file_id: str,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FileRecord).where(
        FileRecord.id == file_id,
        FileRecord.teacher_id == current_user.id,
    )
    res = await db.execute(stmt)
    file_rec = res.scalar_one_or_none()
    if not file_rec:
        raise NotFoundError(f"File {file_id} not found in your private library")

    # Fetch chunk summary
    chunk_stmt = select(ChunkRecord).where(ChunkRecord.file_id == file_id)
    chunk_res = await db.execute(chunk_stmt)
    chunks = chunk_res.scalars().all()

    return {
        "id": file_rec.id,
        "filename": file_rec.filename,
        "file_size": file_rec.file_size,
        "status": file_rec.status,
        "metadata": file_rec.meta_json,
        "total_chunks": len(chunks),
        "chunks_preview": [
            {
                "id": c.id,
                "page_number": c.page_number,
                "chapter": c.chapter,
                "topic": c.topic,
                "kind": c.kind,
                "content_snippet": c.content[:200] + "..." if len(c.content) > 200 else c.content,
            }
            for c in chunks[:10]
        ],
        "created_at": file_rec.created_at,
    }


@router.delete("/files/{file_id}")
async def delete_teacher_file(
    file_id: str,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FileRecord).where(
        FileRecord.id == file_id,
        FileRecord.teacher_id == current_user.id,
    )
    res = await db.execute(stmt)
    file_rec = res.scalar_one_or_none()
    if not file_rec:
        raise NotFoundError("File not found")

    # Delete local file if exists
    if os.path.exists(file_rec.file_path):
        try:
            os.remove(file_rec.file_path)
        except Exception:
            pass

    # Delete chunks and record
    await db.execute(delete(ChunkRecord).where(ChunkRecord.file_id == file_id))
    await db.delete(file_rec)
    await db.commit()

    return {"message": "File and indexed chunks deleted successfully"}


@router.get("/search")
async def search_library(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    chapter: Optional[str] = None,
    kind: Optional[str] = None,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Rules.md A.3 & A.4: Hybrid search inside teacher's own files with teacher-only source label
    results = await hybrid_search.search_teacher_library(
        db=db,
        teacher_id=current_user.id,
        query=query,
        top_k=top_k,
        chapter_filter=chapter,
        kind_filter=kind,
    )

    return {
        "query": query,
        "results_count": len(results),
        "results": results,
    }


@router.get("/syllabus")
async def get_syllabus_tree(
    board: Optional[str] = None,
    class_level: Optional[int] = None,
    subject_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nodes = await syllabus_service.get_all_syllabus_nodes(
        db=db,
        board=board,
        class_level=class_level,
        subject_name=subject_name,
    )
    if not nodes:
        await syllabus_service.seed_syllabus_if_empty(db)
        nodes = await syllabus_service.get_all_syllabus_nodes(
            db=db,
            board=board,
            class_level=class_level,
            subject_name=subject_name,
        )

    # Group hierarchically by board -> class -> subject -> chapter -> topics
    tree: dict[str, Any] = {}
    for n in nodes:
        b_key = n.board
        c_key = f"Class {n.class_level}"
        s_key = n.subject_name
        ch_key = n.chapter

        if b_key not in tree:
            tree[b_key] = {}
        if c_key not in tree[b_key]:
            tree[b_key][c_key] = {}
        if s_key not in tree[b_key][c_key]:
            tree[b_key][c_key][s_key] = {}
        if ch_key not in tree[b_key][c_key][s_key]:
            tree[b_key][c_key][s_key][ch_key] = []

        if n.topic not in tree[b_key][c_key][s_key][ch_key]:
            tree[b_key][c_key][s_key][ch_key].append(n.topic)

    return {
        "total_nodes": len(nodes),
        "tree": tree,
    }
