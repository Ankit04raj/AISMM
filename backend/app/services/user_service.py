"""User service - Business logic for user management."""

from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import User, SocialAccount
from backend.app.core.errors import NotFoundError, ValidationError


class UserService:
    """Service for managing users."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).
            options(selectinload(User.social_accounts)).
            where(User.id == user_id).
        )
        return result.scalar_one_or_none()

    async def get_users(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get paginated users."""
        query = select(User).
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).
        query = query.limit(page_size)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        result = await self.db.execute(query)
        users = result.scalars().all()

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": (page * page_size) < total,
        }

    async def update_user(self, user_id: UUID, name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """Update a user."""
        user = await self.get_user(user_id)
        if not user:
            return None

        if name:
            user.name = name
        if email:
            user.email = email
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user and their social accounts."""
        user = await self.get_user(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True