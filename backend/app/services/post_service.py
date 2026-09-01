"""Post service - Business logic for post management and multi-platform publishing."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
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
from backend.app.core.normalization import (
    ContentNormalizer,
    UniversalContent,
    ContentType,
    MediaType,
    UniversalMedia,
)
from backend.app.core.schemas.post import (
    CreatePostRequest,
    MultiPlatformPostRequest,
    PostResponse,
    MultiPlatformPostResponse,
    PlatformCustomization,
)
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError


class PostService:
    """Service for managing posts, multi-platform publishing, and scheduling."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(
        self,
        user_id: UUID,
        request: CreatePostRequest,
    ) -> PostResponse:
        """Create and optionally publish a post to a single platform."""
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

    async def create_multi_platform_post(
        self,
        user_id: UUID,
        request: MultiPlatformPostRequest,
    ) -> MultiPlatformPostResponse:
        """Create once -> customize per platform -> publish/schedule to all selected platforms."""
        # 1. Validate all platforms
        for p in request.platforms:
            if not PlatformRegistry.is_registered(p):
                raise ValidationError(f"Unsupported platform: {p}")

        content_type_map = {
            "post": ContentType.POST,
            "reel": ContentType.REEL,
            "story": ContentType.STORY,
            "carousel": ContentType.CAROUSEL,
        }
        ct = content_type_map.get(request.content_type.lower(), ContentType.POST)
        db_content_type = getattr(ContentTypeEnum, ct.name, ContentTypeEnum.POST)

        base_media_items = [
            ContentNormalizer.normalize_media(m.model_dump() if hasattr(m, "model_dump") else m.dict())
            for m in request.media
        ]

        # Create master post record
        post = Post(
            user_id=user_id,
            content_type=db_content_type,
            text=request.text,
            caption=request.caption,
            hashtags=request.hashtags,
            mentions=request.mentions,
            status=PostStatusEnum.SCHEDULED if (request.scheduled_at and not request.publish_now) else PostStatusEnum.PUBLISHING,
            scheduled_at=request.scheduled_at,
        )
        self.db.add(post)
        await self.db.flush()

        # Save base media items
        for m in base_media_items:
            self.db.add(
                PostMedia(
                    post_id=post.id,
                    media_type=m.type.value if hasattr(m.type, "value") else str(m.type),
                    url=m.url,
                    thumbnail_url=m.thumbnail_url,
                    duration_seconds=m.duration_seconds,
                    title=m.title,
                    caption=m.caption,
                    alt_text=m.alt_text,
                )
            )

        platform_results: Dict[str, PostResponse] = {}
        all_success = True

        for platform in request.platforms:
            p_key = platform.lower()
            adapter = PlatformRegistry.get_adapter(p_key)
            custom = request.customizations.get(p_key, PlatformCustomization())

            # Prepare effective fields for this platform
            caption = custom.caption or request.caption or request.text or ""
            text = custom.text or request.text or caption
            hashtags = custom.hashtags if custom.hashtags is not None else request.hashtags
            mentions = custom.mentions if custom.mentions is not None else request.mentions
            media_list = [
                ContentNormalizer.normalize_media(m.model_dump() if hasattr(m, "model_dump") else m.dict())
                for m in (custom.media if custom.media is not None else request.media)
            ]

            universal_content = UniversalContent(
                content_type=ct,
                text=text,
                caption=caption,
                hashtags=hashtags,
                mentions=mentions,
                media=media_list,
                scheduled_at=request.scheduled_at,
                platform_data=custom.options or {},
            )

            try:
                if request.scheduled_at and not request.publish_now:
                    res = await adapter.schedule_post(universal_content, request.scheduled_at)
                else:
                    res = await adapter.publish_post(universal_content)

                pub = PostPublication(
                    post_id=post.id,
                    platform=p_key,
                    platform_post_id=res.platform_post_id or None,
                    permalink=res.url,
                    media_type=(res.platform_data or {}).get("media_type", ct.value),
                    scheduled_at=request.scheduled_at,
                    published_at=res.published_at if res.status == "published" else None,
                    platform_data=res.platform_data or {},
                    status=res.status,
                )
                self.db.add(pub)

                platform_results[p_key] = PostResponse(
                    id=res.platform_post_id or str(post.id),
                    platform=p_key,
                    permalink=res.url,
                    media_type=(res.platform_data or {}).get("media_type", ct.value),
                    published_at=res.published_at if isinstance(res.published_at, datetime) else None,
                    scheduled_at=request.scheduled_at,
                    status=res.status,
                    platform_data=res.platform_data or {},
                )
            except Exception as e:
                all_success = False
                pub = PostPublication(
                    post_id=post.id,
                    platform=p_key,
                    status="failed",
                    error_message=str(e),
                )
                self.db.add(pub)
                platform_results[p_key] = PostResponse(
                    id=str(post.id),
                    platform=p_key,
                    status="failed",
                    platform_data={"error": str(e)},
                )

        if all_success:
            post.status = PostStatusEnum.PUBLISHED if request.publish_now else PostStatusEnum.SCHEDULED
            if request.publish_now:
                post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            post.status = PostStatusEnum.FAILED

        await self.db.commit()
        await self.db.refresh(post)

        return MultiPlatformPostResponse(
            post_id=str(post.id),
            overall_status=post.status.value,
            results=platform_results,
            created_at=post.created_at or datetime.now(timezone.utc),
        )

    async def retry_publication(
        self,
        post_id: UUID,
        user_id: UUID,
        platform: str,
    ) -> PostResponse:
        """Retry publishing a failed platform publication for an existing post."""
        post = await self.get_post(post_id, user_id)
        if not post:
            raise NotFoundError("Post not found")

        pub = next((p for p in post.publications if p.platform.lower() == platform.lower()), None)
        if not pub:
            raise NotFoundError(f"No publication found for platform {platform}")

        adapter = PlatformRegistry.get_adapter(platform)
        if not adapter:
            raise PlatformError(f"Adapter not available for {platform}")

        universal_content = UniversalContent(
            content_type=ContentType(post.content_type.value) if hasattr(post.content_type, "value") else ContentType.POST,
            text=post.text,
            caption=post.caption,
            hashtags=post.hashtags or [],
            mentions=post.mentions or [],
            media=[
                UniversalMedia(
                    type=MediaType(m.media_type) if isinstance(m.media_type, str) else m.media_type,
                    url=m.url,
                    thumbnail_url=m.thumbnail_url,
                )
                for m in post.media
            ],
        )

        res = await adapter.publish_post(universal_content)

        pub.platform_post_id = res.platform_post_id or None
        pub.permalink = res.url
        pub.status = res.status
        pub.error_message = None
        pub.published_at = res.published_at if isinstance(res.published_at, datetime) else datetime.now(timezone.utc).replace(tzinfo=None)
        pub.platform_data = res.platform_data or {}

        # If all publications are now published, update parent post status
        if all(p.status == "published" for p in post.publications):
            post.status = PostStatusEnum.PUBLISHED
            post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.db.commit()

        return PostResponse(
            id=res.platform_post_id or str(post.id),
            platform=platform,
            permalink=res.url,
            status=res.status,
            published_at=pub.published_at,
            platform_data=res.platform_data or {},
        )

    async def get_post(self, post_id: UUID, user_id: UUID) -> Optional[Post]:
        """Get a post by ID with all relations."""
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
        """Delete a post from DB and all platforms."""
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
