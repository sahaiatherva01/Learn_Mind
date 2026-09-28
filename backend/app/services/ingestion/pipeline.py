import uuid
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models import ChunkRecord, FileRecord
from app.services.ingestion.parser import pdf_parser
from app.services.ingestion.syllabus import syllabus_service
from app.services.retrieval.embeddings import embedding_service


class IngestionPipeline:
    """
    G1 Ingestion Graph:
    parse -> clean -> chunk -> embed -> detect chapters/topics -> store -> update status
    """

    @classmethod
    async def process_file(
        cls,
        db: AsyncSession,
        file_id: str,
        file_bytes: bytes,
    ) -> Dict[str, Any]:
        stmt = select(FileRecord).where(FileRecord.id == file_id)
        res = await db.execute(stmt)
        file_record = res.scalar_one_or_none()
        if not file_record:
            raise ValueError(f"FileRecord {file_id} not found")

        try:
            logger.info(f"Starting ingestion for file {file_record.filename} (ID: {file_id})")

            # 1. Parse pages
            pages = pdf_parser.parse_pdf_pages(file_bytes)
            if not pages:
                raise ValueError("PDF contains no extractable text")

            # 2. Fetch syllabus nodes for tagging
            syllabus_nodes = await syllabus_service.get_all_syllabus_nodes(db)
            if not syllabus_nodes:
                await syllabus_service.seed_syllabus_if_empty(db)
                syllabus_nodes = await syllabus_service.get_all_syllabus_nodes(db)

            total_chunks_created = 0
            detected_chapters = set()
            detected_topics = set()

            # 3. Process each page and create chunks
            for page_info in pages:
                page_num = page_info["page_number"]
                page_text = page_info["text"]
                if not page_text:
                    continue

                raw_chunks = pdf_parser.chunk_page_content(page_num, page_text)

                for chunk_data in raw_chunks:
                    content = chunk_data["content"]
                    kind = chunk_data["kind"]

                    # Tag chapter/topic
                    subj, chapter, topic, class_lvl = syllabus_service.match_chapter_topic(
                        content, syllabus_nodes
                    )
                    if chapter:
                        detected_chapters.add(chapter)
                    if topic:
                        detected_topics.add(topic)

                    # Generate embedding
                    embedding = embedding_service.get_embedding(content)

                    # Save ChunkRecord
                    chunk = ChunkRecord(
                        id=str(uuid.uuid4()),
                        file_id=file_record.id,
                        teacher_id=file_record.teacher_id,
                        page_number=page_num,
                        chapter=chapter,
                        topic=topic,
                        kind=kind,
                        content=content,
                        embedding_json=embedding,
                    )
                    db.add(chunk)
                    total_chunks_created += 1

            # 4. Update FileRecord to READY
            file_record.status = "READY"
            file_record.meta_json = {
                "pages_count": len(pages),
                "chunks_count": total_chunks_created,
                "detected_chapters": list(detected_chapters),
                "detected_topics": list(detected_topics),
            }

            await db.commit()
            await db.refresh(file_record)
            logger.info(f"Ingestion completed for file {file_id}. Chunks: {total_chunks_created}")

            return {
                "file_id": file_id,
                "status": "READY",
                "chunks_count": total_chunks_created,
                "chapters": list(detected_chapters),
                "topics": list(detected_topics),
            }

        except Exception as e:
            logger.error(f"Ingestion failed for file {file_id}: {str(e)}")
            file_record.status = "FAILED"
            file_record.meta_json = {"error": str(e)}
            await db.commit()
            raise


ingestion_pipeline = IngestionPipeline()
