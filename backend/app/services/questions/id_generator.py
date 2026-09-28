# Question ID generation & Query resolver per Rules.md B.1-B.7
import random
import re
from typing import NamedTuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Question
from app.services.generation.subject_packs import subject_pack_manager

# Crockford-style Base32 characters excluding confusing characters (0, 1, I, L, O)
BASE32_ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"


class ResolvedQuery(NamedTuple):
    query_type: str  # "SHORT_ID", "SHORT_ID_VERSION", "LONG_ID", "TEXT"
    short_id: str | None
    version: int | None
    long_id: str | None
    text_query: str | None


class QuestionIDService:
    """
    Handles generation of immutable Short IDs and Long IDs, and parsing search queries.
    Rules.md B.1: Long ID and Short ID at creation.
    Rules.md B.6: Search resolves long ID, short ID, or short@vN.
    """

    @staticmethod
    def generate_short_id(length: int = 6) -> str:
        """
        Generates a 6-character Base32 short ID with prefix Q- (e.g. Q-8K3F2A).
        """
        token = "".join(random.choices(BASE32_ALPHABET, k=length))
        return f"Q-{token}"

    @classmethod
    async def generate_unique_short_id(cls, db: AsyncSession) -> str:
        """
        Generates a collision-free Short ID against the database.
        """
        for _ in range(10):
            candidate = cls.generate_short_id()
            result = await db.execute(select(Question.id).where(Question.short_id == candidate))
            if result.scalar_one_or_none() is None:
                return candidate
        # Fallback with extra length if collision occurs repeatedly
        return f"Q-{''.join(random.choices(BASE32_ALPHABET, k=8))}"

    @classmethod
    async def generate_long_id(
        cls,
        db: AsyncSession,
        subject: str,
        class_level: int,
        chapter: str,
        topic: str,
    ) -> str:
        """
        Generates Long ID: SUBJECT-CLASS-CHAPTER-TOPIC-SEQ
        Example: MTH-12-CAL-DEF-000482
        """
        sub_code = subject_pack_manager.get_subject_code(subject)
        chap_code = subject_pack_manager.get_chapter_code(subject, chapter)
        top_code = subject_pack_manager.get_topic_code(subject, chapter, topic)
        class_str = str(class_level).zfill(2)

        prefix = f"{sub_code}-{class_str}-{chap_code}-{top_code}"

        # Get count of existing questions with this prefix to assign sequence number
        stmt = select(func.count(Question.id)).where(Question.long_id.like(f"{prefix}-%"))
        result = await db.execute(stmt)
        count = result.scalar() or 0
        seq_num = count + 1
        seq_str = str(seq_num).zfill(6)

        return f"{prefix}-{seq_str}"

    @staticmethod
    def parse_query(raw_query: str) -> ResolvedQuery:
        """
        Parses search strings to detect Short ID, Short ID with version, Long ID, or general text.
        Examples:
        - "Q-8K3F2A" -> SHORT_ID
        - "Q-8K3F2A@v2" or "Q-8K3F2A@2" -> SHORT_ID_VERSION (version 2)
        - "MTH-12-CAL-DEF-000482" -> LONG_ID
        - "find questions on calculus integration" -> TEXT
        """
        query = raw_query.strip()

        # Check Short ID with version (e.g. Q-8K3F2A@v2 or Q-8K3F2A@2)
        match_short_ver = re.match(r"^(Q-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{6,8})@v?([0-9]+)$", query, re.IGNORECASE)
        if match_short_ver:
            return ResolvedQuery(
                query_type="SHORT_ID_VERSION",
                short_id=match_short_ver.group(1).upper(),
                version=int(match_short_ver.group(2)),
                long_id=None,
                text_query=None,
            )

        # Check plain Short ID (e.g. Q-8K3F2A)
        match_short = re.match(r"^(Q-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{6,8})$", query, re.IGNORECASE)
        if match_short:
            return ResolvedQuery(
                query_type="SHORT_ID",
                short_id=match_short.group(1).upper(),
                version=None,
                long_id=None,
                text_query=None,
            )

        # Check Long ID format: ABC-12-DEF-GHI-000123
        match_long = re.match(r"^[A-Z0-9]{2,4}-[0-9]{2}-[A-Z0-9]{2,4}-[A-Z0-9]{2,4}-[0-9]{4,6}$", query, re.IGNORECASE)
        if match_long:
            return ResolvedQuery(
                query_type="LONG_ID",
                short_id=None,
                version=None,
                long_id=query.upper(),
                text_query=None,
            )

        # Free text search
        return ResolvedQuery(
            query_type="TEXT",
            short_id=None,
            version=None,
            long_id=None,
            text_query=query,
        )


question_id_service = QuestionIDService()
