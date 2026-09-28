# Job queue abstraction per ARCH.md §2 and Rules.md G.7
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import JobRecord


class JobQueue:
    @staticmethod
    async def enqueue(
        db: AsyncSession,
        job_type: str,
        payload: Dict[str, Any],
        run_at: Optional[datetime] = None,
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
