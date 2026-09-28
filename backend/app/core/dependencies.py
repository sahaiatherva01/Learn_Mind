from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import UserRole, UserStatus, decode_access_token
from app.db.models import User
from app.db.session import get_db


async def get_token_header(authorization: str | None = Header(None)) -> str:
    if not authorization:
        raise UnauthorizedError("Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format. Expected 'Bearer <token>'")
    return parts[1]


async def get_current_user(
    token: str = Depends(get_token_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token subject")

    stmt = select(User).where(User.id == str(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found or has been removed")

    if user.status == UserStatus.SUSPENDED.value or user.status == UserStatus.REJECTED.value:
        raise ForbiddenError(f"Account is {user.status.lower()}")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status != UserStatus.ACTIVE.value:
        raise ForbiddenError("Account is pending approval from school incharge or admin")
    return current_user


def require_roles(allowed_roles: list[UserRole]) -> Callable:
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if (
            current_user.status != UserStatus.ACTIVE.value
            and current_user.role != UserRole.ADMIN.value
        ):
            raise ForbiddenError("Account is pending approval")

        if current_user.role not in [r.value for r in allowed_roles]:
            raise ForbiddenError(
                f"Role '{current_user.role}' is not authorized to access this resource"
            )
        return current_user

    return role_checker


# Role shortcut dependencies
require_admin = require_roles([UserRole.ADMIN])
require_incharge = require_roles([UserRole.ADMIN, UserRole.INCHARGE])
require_class_teacher = require_roles([UserRole.ADMIN, UserRole.INCHARGE, UserRole.CLASS_TEACHER])
require_teacher = require_roles(
    [
        UserRole.ADMIN,
        UserRole.INCHARGE,
        UserRole.CLASS_TEACHER,
        UserRole.SUBJECT_TEACHER,
    ]
)
require_student = require_roles([UserRole.STUDENT])
