"""Post service - Business logic for post management and multi-platform publishing."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.services.owned_adapter import owned_adapter
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

    async def create_post(self, user_id: UUID, request: CreatePostRequest) -> PostResponse:
        data = request.model_dump()
        data.pop('platform', None)
        response = await self.create_multi_platform_post(user_id, MultiPlatformPostRequest(
            platforms=[request.platform], **data))
        result = response.results[request.platform]
        result.id = response.post_id
        return result

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

        import ipaddress
        from urllib.parse import urlparse
        from backend.app.config import get_settings
        settings = get_settings()
        all_media = list(request.media)
        for customization in request.customizations.values():
            all_media.extend(customization.media or [])
        for media in all_media:
            parsed = urlparse(media.url)
            if parsed.scheme != 'https' or parsed.username or parsed.password:
                raise ValidationError('Media URLs must use HTTPS without embedded credentials')
            host = (parsed.hostname or '').lower()
            if not host:
                raise ValidationError('Media URL must contain a valid hostname')
            if host in {'localhost', '127.0.0.1', '::1', '0.0.0.0'}:
                raise ValidationError('Media URL cannot target localhost or loopback addresses')
            try:
                ip = ipaddress.ip_address(host)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                    raise ValidationError('Media URL cannot target private or internal network addresses')
            except ValueError:
                pass
            if settings.ENVIRONMENT != 'development' and host not in settings.MEDIA_ALLOWED_HOSTS:
                raise ValidationError('Media host is not in the operator-approved allowlist')
        adapters = {platform: await owned_adapter(self.db, user_id, platform) for platform in request.platforms}
        if not request.text and not request.caption and not request.media:
            raise ValidationError('Post content is required')
        if request.scheduled_at:
            value = request.scheduled_at
            if value.tzinfo is None:
                raise ValidationError('Scheduled time must include a timezone')
            if value <= datetime.now(timezone.utc):
                raise ValidationError('Scheduled time must be in the future')
            request.scheduled_at = value.astimezone(timezone.utc).replace(tzinfo=None)
        if not request.publish_now and not request.scheduled_at:
            raise ValidationError('A scheduled time is required when publish_now is false')

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
            id=uuid4(),
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
            adapter = adapters[p_key]
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
                    # Queue locally; never pre-publish and then publish again in the worker.
                    from types import SimpleNamespace
                    res = SimpleNamespace(platform_post_id=None, url=None, platform_data={}, status='scheduled', published_at=None)
                else:
                    res = await adapter.publish_post(universal_content)
                    if res.status != 'published' or not res.platform_post_id:
                        raise ValidationError('Platform did not confirm publication')

                if isinstance(res.published_at, str):
                    res.published_at = datetime.fromisoformat(res.published_at.replace('Z', '+00:00'))
                pub = PostPublication(
                    post_id=post.id,
                    platform=p_key,
                    platform_post_id=res.platform_post_id or None,
                    permalink=res.url,
                    media_type=(res.platform_data or {}).get("media_type", ct.value),
                    scheduled_at=request.scheduled_at,
                    published_at=res.published_at.replace(tzinfo=None) if res.status == "published" and res.published_at else None,
                    platform_data={"content": universal_content.to_dict()},
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
                    error_message="Platform publication failed. Review provider permissions before retrying.",
                )
                self.db.add(pub)
                platform_results[p_key] = PostResponse(
                    id=str(post.id),
                    platform=p_key,
                    status="failed",
                    platform_data={"error": "Platform publication failed; no successful publication was confirmed."},
                )

        if all_success:
            post.status = PostStatusEnum.PUBLISHED if request.publish_now else PostStatusEnum.SCHEDULED
            if request.publish_now:
                post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            post.status = PostStatusEnum.FAILED

        if all_success and not request.publish_now:
            from backend.app.db.models import Schedule
            self.db.add(Schedule(user_id=user_id, post_id=post.id,
                                 scheduled_at=request.scheduled_at, status='pending'))

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

        if pub.status != 'failed':
            raise ValidationError('Only failed publications can be retried')
        adapter = await owned_adapter(self.db, user_id, platform)
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
            if publication.platform_post_id:
                adapter = await owned_adapter(self.db, user_id, publication.platform)
                if not await adapter.delete_post(publication.platform_post_id):
                    raise PlatformError('Platform deletion not confirmed; local post retained')

        await self.db.delete(post)
        await self.db.commit()
        return True
