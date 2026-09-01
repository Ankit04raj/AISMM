"""Post service - Business logic for post management."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import (
    Post,
    PostPublication,
    PostMedia,
    User,
    SocialAccount,
    ContentTypeEnum,
    PostStatusEnum,
)
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import ContentNormalizer, UniversalContent, ContentType, MediaType, UniversalMedia
from backend.app.core.schemas.post import CreatePostRequest, PostResponse, PostMetrics
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError


class PostService:
    """Service for managing posts and publications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(
        self,
        user_id: UUID,
        request: CreatePostRequest,
    ) -> PostResponse:
        """Create and optionally publish a post."""
        if not PlatformRegistry.is_registered(request.platform):
            raise ValidationError(f"Unsupported platform: {request.platform}")

        adapter = PlatformRegistry.get_adapter(request.platform)
        if not adapter:
            raise PlatformError(f"Adapter not available for {request.platform}")

        content_type_map = {
            "post": ContentType.POST,
            "reel": ContentType.REEL,
            "story": ContentType.STORY,
            "carousel": ContentType.CAROUSEL,
        }
        ct = content_type_map.get(request.content_type.lower(), ContentType.POST)

        media_items = [
            ContentNormalizer.normalize_media(m.model_dump() if hasattr(m, "model_dump") else m.dict())
            for m in (request.media or [])
        ]

        universal_content = UniversalContent(
            content_type=ct,
            text=request.text,
            caption=request.caption,
            hashtags=request.hashtags or [],
            mentions=request.mentions or [],
            media=media_items,
            location_id=request.location_id,
            scheduled_at=request.scheduled_at,
        )

        if request.scheduled_at and not request.publish_now:
            result = await adapter.schedule_post(universal_content, request.scheduled_at)
        else:
            result = await adapter.publish_post(universal_content)

        db_content_type = getattr(ContentTypeEnum, ct.name, ContentTypeEnum.POST)
        is_published = result.status == "published"
        db_status = PostStatusEnum.PUBLISHED if is_published else PostStatusEnum.SCHEDULED

        post = Post(
            user_id=user_id,
            content_type=db_content_type,
            text=request.text,
            caption=request.caption,
            hashtags=request.hashtags or [],
            mentions=request.mentions or [],
            status=db_status,
            scheduled_at=request.scheduled_at,
            published_at=result.published_at if is_published else None,
            platform_data=result.platform_data or {},
        )
        self.db.add(post)
        await self.db.flush()

        for media in media_items:
            post_media = PostMedia(
                post_id=post.id,
                media_type=media.type.value if hasattr(media.type, "value") else str(media.type),
                url=media.url,
                thumbnail_url=media.thumbnail_url,
                duration_seconds=media.duration_seconds,
                width=media.width,
                height=media.height,
                title=media.title,
                caption=media.caption,
                alt_text=media.alt_text,
                file_size_bytes=media.file_size_bytes,
                mime_type=media.mime_type,
            )
            self.db.add(post_media)

        container_id = (result.platform_data or {}).get("container_id")
        publication = PostPublication(
            post_id=post.id,
            platform=request.platform,
            platform_post_id=result.platform_post_id or None,
            platform_container_id=container_id,
            permalink=result.url,
            media_type=(result.platform_data or {}).get("media_type", ct.value),
            scheduled_at=request.scheduled_at,
            published_at=result.published_at if is_published else None,
            platform_data=result.platform_data or {},
            status=result.status,
        )
        self.db.add(publication)

        await self.db.commit()
        await self.db.refresh(post)

        published_dt = None
        if result.published_at:
            published_dt = datetime.fromisoformat(result.published_at) if isinstance(result.published_at, str) else result.published_at

        return PostResponse(
            id=result.platform_post_id or str(post.id),
            platform=request.platform,
            permalink=result.url,
            media_type=(result.platform_data or {}).get("media_type", ct.value),
            published_at=published_dt,
            scheduled_at=request.scheduled_at,
            status=publication.status,
            platform_data=result.platform_data or {},
        )

    async def get_post(self, post_id: UUID, user_id: UUID) -> Optional[Post]:
        """Get a post by ID."""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.media),
                selectinload(Post.publications),
                selectinload(Post.comments),
                selectinload(Post.metrics),
            )
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_posts(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Get paginated posts."""
        query = (
            select(Post)
            .options(
                selectinload(Post.media),
                selectinload(Post.publications),
            )
            .where(Post.user_id == user_id)
        )

        if status:
            status_enum = getattr(PostStatusEnum, status.upper(), None)
            if status_enum:
                query = query.where(Post.status == status_enum)

        if platform:
            query = query.join(PostPublication).where(PostPublication.platform == platform)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Post.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        posts = result.scalars().all()

        return {
            "posts": posts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": (page * page_size) < total,
        }

    async def delete_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Delete a post from DB and platform."""
        post = await self.get_post(post_id, user_id)
        if not post:
            return False

        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_post_id:
                try:
                    await adapter.delete_post(publication.platform_post_id)
                except Exception:
                    pass

        await self.db.delete(post)
        await self.db.commit()
        return True
