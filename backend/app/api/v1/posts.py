"""Posts API router."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.post_service import PostService
from backend.app.core.schemas.post import (
    CreatePostRequest,
    PostResponse,
    PostListResponse,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create and publish/schedule a post for the authenticated user."""
    service = PostService(db)
    return await service.create_post(current_user.id, request)


@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 20,
    platform: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List posts with pagination for the authenticated user."""
    service = PostService(db)
    result = await service.get_posts(
        user_id=current_user.id,
        status=status_filter,
        platform=platform,
        page=page,
        page_size=page_size,
    )

    posts_responses = []
    for p in result["posts"]:
        pub = p.publications[0] if p.publications else None
        posts_responses.append(
            PostResponse(
                id=str(p.id),
                platform=pub.platform if pub else "unknown",
                permalink=pub.permalink if pub else None,
                media_type=pub.media_type if pub else (p.content_type.value if hasattr(p.content_type, "value") else str(p.content_type)),
                published_at=pub.published_at if pub else None,
                scheduled_at=p.scheduled_at,
                status=p.status.value if hasattr(p.status, "value") else str(p.status),
                platform_data=pub.platform_data if pub else {},
            )
        )

    return PostListResponse(
        posts=posts_responses,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        has_next=result["has_next"],
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single post by ID owned by the authenticated user."""
    service = PostService(db)
    post = await service.get_post(UUID(post_id), current_user.id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    pub = post.publications[0] if post.publications else None
    return PostResponse(
        id=str(post.id),
        platform=pub.platform if pub else "unknown",
        permalink=pub.permalink if pub else None,
        media_type=pub.media_type if pub else (post.content_type.value if hasattr(post.content_type, "value") else str(post.content_type)),
        published_at=pub.published_at if pub else None,
        scheduled_at=post.scheduled_at,
        status=post.status.value if hasattr(post.status, "value") else str(post.status),
        platform_data=pub.platform_data if pub else {},
    )


@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a post owned by the authenticated user."""
    service = PostService(db)
    deleted = await service.delete_post(UUID(post_id), current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"deleted": True, "id": post_id}
