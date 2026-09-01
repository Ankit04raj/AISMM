"""Platform-Specific Post Preview Engine."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.core.normalization import (
    UniversalContent,
    UniversalMedia,
    ContentType,
    MediaType,
    ContentNormalizer,
)
from backend.app.core.schemas.post import (
    ContentPreviewRequest,
    ContentPreviewResponse,
    PlatformCustomization,
)


class PreviewService:
    """Renders native preview models for social media platforms."""

    @classmethod
    def generate_previews(cls, request: ContentPreviewRequest) -> ContentPreviewResponse:
        previews: Dict[str, Dict[str, Any]] = {}
        all_warnings: Dict[str, List[str]] = {}

        for platform in request.platforms:
            platform_key = platform.lower()
            custom = request.customizations.get(platform_key, PlatformCustomization())

            # Prepare effective fields for this platform
            caption = custom.caption if custom.caption is not None else (request.caption or request.text or "")
            text = custom.text if custom.text is not None else (custom.caption if custom.caption is not None else (request.text or caption))
            hashtags = custom.hashtags if custom.hashtags is not None else request.hashtags
            mentions = custom.mentions if custom.mentions is not None else request.mentions
            media_list = custom.media if custom.media is not None else request.media

            content_type_map = {
                "post": ContentType.POST,
                "reel": ContentType.REEL,
                "story": ContentType.STORY,
                "carousel": ContentType.CAROUSEL,
            }
            ct = content_type_map.get(request.content_type.lower(), ContentType.POST)

            universal_content = UniversalContent(
                content_type=ct,
                text=text,
                caption=caption,
                hashtags=hashtags or [],
                mentions=mentions or [],
                media=[
                    ContentNormalizer.normalize_media(m.model_dump() if hasattr(m, "model_dump") else m.dict())
                    for m in media_list
                ],
            )

            # Validate against platform rules
            warnings = ContentNormalizer.validate_for_platform(universal_content, platform_key)
            all_warnings[platform_key] = warnings

            # Generate native render data
            if platform_key == "instagram":
                previews[platform_key] = cls._preview_instagram(universal_content, custom)
            elif platform_key == "facebook":
                previews[platform_key] = cls._preview_facebook(universal_content, custom)
            elif platform_key == "twitter":
                previews[platform_key] = cls._preview_twitter(universal_content, custom)
            elif platform_key == "linkedin":
                previews[platform_key] = cls._preview_linkedin(universal_content, custom)
            else:
                previews[platform_key] = cls._preview_generic(universal_content, platform_key)

        return ContentPreviewResponse(previews=previews, warnings=all_warnings)

    @classmethod
    def _preview_instagram(cls, content: UniversalContent, custom: PlatformCustomization) -> Dict[str, Any]:
        tag_str = " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])
        mention_str = " ".join([f"@{m.lstrip('@')}" for m in content.mentions[:20]])
        full_caption = content.caption or content.text or ""
        if tag_str:
            full_caption += f"\n\n{tag_str}"
        if mention_str:
            full_caption += f" {mention_str}"

        media_type = ContentNormalizer._determine_instagram_media_type(content)

        return {
            "platform": "instagram",
            "layout": "instagram_card",
            "media_type": media_type,
            "caption": full_caption[:2200],
            "char_count": len(full_caption),
            "max_chars": 2200,
            "media_items": [
                {
                    "type": m.type.value if hasattr(m.type, "value") else str(m.type),
                    "url": m.url,
                    "thumbnail_url": m.thumbnail_url,
                }
                for m in content.media
            ],
            "carousel_count": len(content.media) if media_type == "CAROUSEL" else 1,
            "aspect_ratio": "1:1" if media_type == "IMAGE" else ("9:16" if media_type in ("REELS", "STORIES") else "4:5"),
        }

    @classmethod
    def _preview_facebook(cls, content: UniversalContent, custom: PlatformCustomization) -> Dict[str, Any]:
        message = content.caption or content.text or ""
        if content.hashtags:
            message += "\n\n" + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])

        return {
            "platform": "facebook",
            "layout": "facebook_feed_card",
            "message": message[:63206],
            "char_count": len(message),
            "max_chars": 63206,
            "media_items": [
                {
                    "type": m.type.value if hasattr(m.type, "value") else str(m.type),
                    "url": m.url,
                }
                for m in content.media
            ],
            "link_preview": custom.options.get("link") if custom.options else None,
        }

    @classmethod
    def _preview_twitter(cls, content: UniversalContent, custom: PlatformCustomization) -> Dict[str, Any]:
        text = content.text or content.caption or ""
        if content.hashtags:
            text += " " + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:10]])
        if content.mentions:
            text += " " + " ".join([f"@{m.lstrip('@')}" for m in content.mentions[:10]])

        return {
            "platform": "twitter",
            "layout": "tweet_card",
            "text": text[:280],
            "char_count": len(text),
            "max_chars": 280,
            "char_remaining": max(0, 280 - len(text)),
            "media_count": len(content.media),
            "media_items": [{"url": m.url} for m in content.media[:4]],
        }

    @classmethod
    def _preview_linkedin(cls, content: UniversalContent, custom: PlatformCustomization) -> Dict[str, Any]:
        commentary = content.text or content.caption or ""
        if content.hashtags:
            commentary += "\n\n" + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])

        return {
            "platform": "linkedin",
            "layout": "linkedin_share_box",
            "commentary": commentary[:3000],
            "char_count": len(commentary),
            "max_chars": 3000,
            "media_items": [{"url": m.url} for m in content.media[:9]],
        }

    @classmethod
    def _preview_generic(cls, content: UniversalContent, platform: str) -> Dict[str, Any]:
        return {
            "platform": platform,
            "layout": "generic_card",
            "text": content.text or content.caption or "",
            "media_count": len(content.media),
            "media_items": [{"url": m.url} for m in content.media],
        }
