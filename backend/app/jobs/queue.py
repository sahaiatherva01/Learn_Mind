# Job queue abstraction per ARCH.md §2 and Rules.md G.7
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobRecord


class JobQueue:
    @staticmethod
    async def enqueue(
        db: AsyncSession,
        job_type: str,
        payload: dict[str, Any],
        run_at: datetime | None = None,
    ) -> JobRecord:
        job = JobRecord(
            id=str(uuid.uuid4()),
            job_type=job_type,
            payload_json=payload,
            status="QUEUED",
            run_at=run_at or datetime.now(timezone.utc),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job


job_queue = JobQueue()
