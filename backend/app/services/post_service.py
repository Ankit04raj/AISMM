"""Post service - Business logic for post management."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import Post, PostPublication, PostMedia, User, SocialAccount
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import ContentNormalizer, UniversalContent
from backend.app.core.schemas.post import CreatePostRequest, PostResponse, PostMetrics
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError


class PostService:
    """Service for managing posts and publications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(
        self,
        user_id: UUID,
        request: CreatePostRequest
    ) -> PostResponse:
        """Create and optionally publish a post."""
        # Validate platform
        if request.platform not in PlatformRegistry.list_platforms():
            raise ValidationError(f"Unsupported platform: {request.platform}")

        # Get or create adapter
        adapter = PlatformRegistry.get_adapter(request.platform)
        if not adapter:
            raise PlatformError(f"Adapter not available for {request.platform}")

        # Normalize content
        universal_content = UniversalContent(
            content_type=request.content_type,
            text=request.text,
            caption=request.caption,
            hashtags=request.hashtags or [],
            mentions=request.mentions or [],
            media=[
                ContentNormalizer.normalize_media(m.dict())
                for m in request.media
            ],
        )

        # Publish or schedule
        if request.scheduled_at and not request.publish_now:
            result = await adapter.schedule_post(
                content=universal_content,
                media_items=universal_content.media,
                scheduled_at=request.scheduled_at,
                media_type=universal_content.content_type,
            )
        else:
            result = await adapter.publish_post(
                content=universal_content,
                options=request.options or {}
            )

        # Save to database
        post = Post(
            user_id=user_id,
            content_type=request.content_type,
            text=request.text,
            caption=request.caption,
            hashtags=request.hashtags,
            mentions=request.mentions,
            status="published" if result.get("post_id") else "scheduled",
        )
        self.db.add(post)
        await self.db.flush()

        # Save media
        for media in request.media:
            post_media = PostMedia(
                post_id=post.id,
                media_type=media.type,
                url=media.url,
                thumbnail_url=media.thumbnail_url,
                duration_seconds=media.duration_seconds,
                width=media.width,
                height=media.height,
                title=media.title,
                caption=media.caption,
                alt_text=media.alt_text,
            )
            self.db.add(post_media)

        # Save publication record
        publication = PostPublication(
            post_id=post.id,
            platform=request.platform,
            platform_post_id=result.get("post_id"),
            platform_container_id=result.get("container_id"),
            permalink=result.get("permalink"),
            media_type=result.get("media_type"),
            scheduled_at=request.scheduled_at,
            published_at=result.get("published_at"),
            platform_data=result.get("platform_data", {}),
            status="published" if result.get("post_id") else "scheduled",
        )
        self.db.add(publication)

        await self.db.commit()
        await self.db.refresh(post)

        return PostResponse(
            id=result.get("post_id", str(post.id)),
            platform=request.platform,
            permalink=result.get("permalink"),
            media_type=result.get("media_type"),
            published_at=result.get("published_at"),
            scheduled_at=request.scheduled_at,
            status=publication.status,
            platform_data=result.get("platform_data", {}),
        )

    async def get_post(self, post_id: UUID, user_id: UUID) -> Optional[Post]:
        """Get a post by ID."""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.media),
                selectinload(Post.publications),
            )
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_posts(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated posts for a user."""
        query = select(Post).where(Post.user_id == user_id)

        if status:
            query = query.where(Post.status == status)

        if platform:
            query = query.join(PostPublication).where(PostPublication.platform == platform)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(Post.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(
            query.options(
                selectinload(Post.media),
                selectinload(Post.publications),
            )
        )
        posts = result.scalars().all()

        return {
            "posts": posts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": (page * page_size) < total,
        }

    async def update_post(
        self,
        post_id: UUID,
        user_id: UUID,
        caption: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Post]:
        """Update a post (caption only for published posts)."""
        post = await self.get_post(post_id, user_id)
        if not post:
            return None

        if post.status == "published":
            # Update on platform
            for publication in post.publications:
                adapter = PlatformRegistry.get_adapter(publication.platform)
                if adapter:
                    await adapter.update_post(
                        post_id=publication.platform_post_id,
                        caption=caption,
                        options=options,
                    )

        post.caption = caption or post.caption
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Delete a post and its publications."""
        post = await self.get_post(post_id, user_id)
        if not post:
            return False

        # Delete from platforms
        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_post_id:
                await adapter.delete_post(publication.platform_post_id)

        await self.db.delete(post)
        await self.db.commit()
        return True

    async def get_post_metrics(self, post_id: UUID, user_id: UUID) -> Optional[PostMetrics]:
        """Get metrics for a post."""
        post = await self.get_post(post_id, user_id)
        if not post:
            return None

        # Get metrics from each platform
        all_metrics = {}
        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_post_id:
                try:
                    metrics = await adapter.fetch_insights(publication.platform_post_id)
                    all_metrics[publication.platform] = metrics
                except Exception:
                    pass

        if not all_metrics:
            return None

        # Combine metrics (simple sum for now)
        combined = {}
        for platform_metrics in all_metrics.values():
            for key, value in platform_metrics.items():
                if isinstance(value, (int, float)):
                    combined[key] = combined.get(key, 0) + value

        return PostMetrics(
            post_id=str(post_id),
            platform=", ".join(all_metrics.keys()),
            impressions=combined.get("impressions"),
            reach=combined.get("reach"),
            likes=combined.get("likes"),
            comments=combined.get("comments"),
            shares=combined.get("shares"),
            saves=combined.get("saves"),
            video_views=combined.get("video_views"),
            engagement_rate=self._calculate_engagement_rate(combined),
            fetched_at=datetime.utcnow(),
        )

    def _calculate_engagement_rate(self, metrics: Dict[str, Any]) -> Optional[float]:
        """Calculate engagement rate from metrics."""
        impressions = metrics.get("impressions", 0)
        if impressions == 0:
            return None

        engagements = sum(
            metrics.get(k, 0)
            for k in ["likes", "comments", "shares", "saves"]
        )
        return round((engagements / impressions) * 100, 2)

    async def get_scheduled_posts(self, user_id: UUID) -> List[Post]:
        """Get all scheduled posts for a user."""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications))
            .where(
                and_(
                    Post.user_id == user_id,
                    Post.status == "scheduled",
                )
            )
            .order_by(Post.created_at)
        )
        return result.scalars().all()

    async def cancel_scheduled_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Cancel a scheduled post."""
        post = await self.get_post(post_id, user_id)
        if not post or post.status != "scheduled":
            return False

        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_container_id:
                await adapter.cancel_scheduled_post(publication.platform_container_id)

        post.status = "cancelled"
        await self.db.commit()
        return True