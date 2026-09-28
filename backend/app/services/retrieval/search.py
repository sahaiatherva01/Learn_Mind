from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChunkRecord, FileRecord
from app.services.retrieval.embeddings import embedding_service


class HybridSearchService:
    @staticmethod
    async def search_teacher_library(
        db: AsyncSession,
        teacher_id: str,
        query: str,
        top_k: int = 5,
        chapter_filter: Optional[str] = None,
        kind_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid semantic and keyword retrieval strictly scoped to the teacher's library.
        Rules.md A.3: Teacher uploads are private to the uploading teacher only.
        """
        # Fetch all chunks for this teacher
        stmt = (
            select(ChunkRecord, FileRecord)
            .join(FileRecord, ChunkRecord.file_id == FileRecord.id)
            .where(ChunkRecord.teacher_id == teacher_id)
        )
        if chapter_filter:
            stmt = stmt.where(ChunkRecord.chapter.ilike(f"%{chapter_filter}%"))
        if kind_filter:
            stmt = stmt.where(ChunkRecord.kind == kind_filter.lower())

        res = await db.execute(stmt)
        rows = res.all()

        if not rows:
            return []

        query_embedding = embedding_service.get_embedding(query)
        scored_results = []

        for chunk, file_rec in rows:
            # 1. Cosine similarity
            chunk_embedding = chunk.embedding_json or []
            cos_sim = embedding_service.cosine_similarity(query_embedding, chunk_embedding)

            # 2. BM25 keyword score
            bm25 = embedding_service.bm25_score(query, chunk.content)

            # 3. Hybrid score (60% vector + 40% keyword)
            hybrid_score = round(0.6 * cos_sim + 0.4 * bm25, 4)

            source_label = f"Book: {file_rec.filename}, Page: {chunk.page_number}"

            scored_results.append(
                {
                    "chunk_id": chunk.id,
                    "file_id": file_rec.id,
                    "filename": file_rec.filename,
                    "page_number": chunk.page_number,
                    "chapter": chunk.chapter,
                    "topic": chunk.topic,
                    "kind": chunk.kind,
                    "content": chunk.content,
                    "score": hybrid_score,
                    "source_label": source_label,  # Teacher only (Rules.md A.4)
                }
            )

        # Sort by score descending and take top_k
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]


hybrid_search = HybridSearchService()
