import uuid
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SyllabusNode


class SyllabusService:
    @staticmethod
    async def seed_syllabus_if_empty(db: AsyncSession) -> int:
        count = await db.scalar(select(func.count(SyllabusNode.id)))
        if count and count > 0:
            return count

        yaml_path = Path(__file__).resolve().parents[2] / "seeds" / "syllabus_pcm_cs.yaml"
        if not yaml_path.exists():
            return 0

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        nodes_added = 0
        order = 0
        for entry in data:
            board = entry.get("board", "ISC")
            class_lvl = entry.get("class_level", 12)
            subj = entry.get("subject_name", "General")

            for ch_data in entry.get("chapters", []):
                chapter_title = ch_data.get("chapter", "General")
                for topic in ch_data.get("topics", []):
                    order += 1
                    node = SyllabusNode(
                        id=str(uuid.uuid4()),
                        board=board,
                        class_level=class_lvl,
                        subject_name=subj,
                        chapter=chapter_title,
                        topic=topic,
                        sequence_order=order,
                    )
                    db.add(node)
                    nodes_added += 1

        await db.commit()
        return nodes_added

    @staticmethod
    async def get_all_syllabus_nodes(
        db: AsyncSession,
        board: Optional[str] = None,
        class_level: Optional[int] = None,
        subject_name: Optional[str] = None,
    ) -> List[SyllabusNode]:
        stmt = select(SyllabusNode)
        if board:
            stmt = stmt.where(SyllabusNode.board == board.upper())
        if class_level:
            stmt = stmt.where(SyllabusNode.class_level == class_level)
        if subject_name:
            stmt = stmt.where(SyllabusNode.subject_name.ilike(f"%{subject_name}%"))
        stmt = stmt.order_by(SyllabusNode.sequence_order.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    def match_chapter_topic(
        text: str,
        nodes: List[SyllabusNode],
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
        """
        Matches text content against syllabus nodes using token overlap.
        Returns: (subject_name, chapter, topic, class_level)
        """
        if not text or not nodes:
            return None, None, None, None

        text_lower = text.lower()
        best_node = None
        best_score = 0

        for node in nodes:
            score = 0
            # Topic match
            topic_words = [w for w in node.topic.lower().split() if len(w) > 3]
            for w in topic_words:
                if w in text_lower:
                    score += 3

            # Chapter match
            ch_words = [w for w in node.chapter.lower().split() if len(w) > 3]
            for w in ch_words:
                if w in text_lower:
                    score += 2

            if score > best_score:
                best_score = score
                best_node = node

        if best_node and best_score >= 2:
            return (
                best_node.subject_name,
                best_node.chapter,
                best_node.topic,
                best_node.class_level,
            )

        return None, None, None, None


syllabus_service = SyllabusService()
