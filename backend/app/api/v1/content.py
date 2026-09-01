"""Content Management and Multi-Platform Publishing API router."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.post_service import PostService
from backend.app.services.preview_service import PreviewService
from backend.app.core.normalization import ContentNormalizer, UniversalContent, ContentType, MediaType
from backend.app.core.schemas.post import (
    MultiPlatformPostRequest,
    MultiPlatformPostResponse,
    ContentPreviewRequest,
    ContentPreviewResponse,
    ContentValidationRequest,
    ContentValidationResponse,
    PostResponse,
)

router = APIRouter(prefix="/content", tags=["Content Management"])

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/preview", response_model=ContentPreviewResponse)
async def generate_content_preview(request: ContentPreviewRequest):
    """Generate platform-specific native previews for composed content."""
    return PreviewService.generate_previews(request)


@router.post("/validate", response_model=ContentValidationResponse)
async def validate_content_constraints(request: ContentValidationRequest):
    """Validate content against character, hashtag, mention, and media limits per platform."""
    platform_warnings = {}
    platform_errors = {}
    is_valid = True

    content_type_map = {
        "post": ContentType.POST,
        "reel": ContentType.REEL,
        "story": ContentType.STORY,
        "carousel": ContentType.CAROUSEL,
    }
    ct = content_type_map.get(request.content_type.lower(), ContentType.POST)

    for platform in request.platforms:
        p_key = platform.lower()
        custom = request.customizations.get(p_key)

        caption = (custom.caption if custom else None) or request.caption or request.text or ""
        text = (custom.text if custom else None) or request.text or caption
        hashtags = (custom.hashtags if custom and custom.hashtags is not None else request.hashtags) or []
        mentions = (custom.mentions if custom and custom.mentions is not None else request.mentions) or []
        media_list = (custom.media if custom and custom.media is not None else request.media) or []

        universal_content = UniversalContent(
            content_type=ct,
            text=text,
            caption=caption,
            hashtags=hashtags,
            mentions=mentions,
            media=[
                ContentNormalizer.normalize_media(m.model_dump() if hasattr(m, "model_dump") else m.dict())
                for m in media_list
            ],
        )

        warnings = ContentNormalizer.validate_for_platform(universal_content, p_key)
        platform_warnings[p_key] = warnings

        errors = []
        if ct == ContentType.CAROUSEL and len(media_list) < 2:
            errors.append("Carousel format requires at least 2 media items")
        if ct == ContentType.CAROUSEL and len(media_list) > 10:
            errors.append("Carousel format cannot exceed 10 media items")

        if errors:
            is_valid = False
        platform_errors[p_key] = errors

    return ContentValidationResponse(
        valid=is_valid,
        platform_warnings=platform_warnings,
        platform_errors=platform_errors,
    )


@router.post("/publish-multi", response_model=MultiPlatformPostResponse, status_code=status.HTTP_201_CREATED)
async def publish_multi_platform(
    request: MultiPlatformPostRequest,
    db: AsyncSession = Depends(get_db),
):
    """Compose and publish/schedule content to multiple social media platforms simultaneously."""
    service = PostService(db)
    return await service.create_multi_platform_post(DEFAULT_USER_ID, request)


@router.post("/{post_id}/retry/{platform}", response_model=PostResponse)
async def retry_failed_platform_publication(
    post_id: str,
    platform: str,
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed publication on a specific platform for an existing post."""
    service = PostService(db)
    return await service.retry_publication(UUID(post_id), DEFAULT_USER_ID, platform)
