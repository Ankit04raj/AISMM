"""Content normalization utilities for cross-platform publishing."""

import re
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from .content import UniversalContent, UniversalMedia, ContentType, MediaType, NormalizedContent


class ContentNormalizer:
    """Normalizes platform-specific content to universal format and vice versa."""

    # Platform-specific character limits
    PLATFORM_LIMITS = {
        "instagram": {
            "caption": 2200,
            "hashtags": 30,
            "mentions": 20,
        },
        "twitter": {
            "text": 280,
            "hashtags": 10,
            "mentions": 10,
        },
        "linkedin": {
            "text": 3000,
            "hashtags": 30,
            "mentions": 20,
        },
        "facebook": {
            "text": 63206,
            "hashtags": 30,
            "mentions": 50,
        },
        "tiktok": {
            "caption": 2200,
            "hashtags": 100,
            "mentions": 20,
        },
    }

    # Platform-specific media requirements
    PLATFORM_MEDIA_SPECS = {
        "instagram": {
            "image": {
                "max_size_mb": 8,
                "formats": ["jpg", "jpeg", "png", "gif", "webp"],
                "aspect_ratios": ["1:1", "4:5", "1.91:1"],
                "max_resolution": (1080, 1350),
            },
            "video": {
                "max_size_mb": 100,
                "formats": ["mp4", "mov"],
                "max_duration_seconds": 60,
                "max_resolution": (1080, 1920),
            },
            "reel": {
                "max_size_mb": 100,
                "formats": ["mp4", "mov"],
                "max_duration_seconds": 90,
                "aspect_ratio": "9:16",
                "max_resolution": (1080, 1920),
            },
            "carousel": {
                "max_items": 10,
                "max_size_mb": 8,
                "formats": ["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov"],
            },
            "story": {
                "max_size_mb": 30,
                "formats": ["jpg", "jpeg", "png", "mp4", "mov"],
                "max_duration_seconds": 60,
                "aspect_ratio": "9:16",
            },
        },
    }

    @classmethod
    def normalize_media(cls, media_dict: Dict[str, Any]) -> UniversalMedia:
        """Normalize a platform media dict to UniversalMedia."""
        media_type = media_dict.get("type", "image")
        try:
            mtype = MediaType(media_type.lower())
        except ValueError:
            mtype = MediaType.IMAGE

        return UniversalMedia(
            type=mtype,
            url=media_dict.get("url", ""),
            thumbnail_url=media_dict.get("thumbnail_url"),
            duration_seconds=media_dict.get("duration_seconds"),
            width=media_dict.get("width"),
            height=media_dict.get("height"),
            title=media_dict.get("title"),
            caption=media_dict.get("caption"),
            alt_text=media_dict.get("alt_text"),
            file_size_bytes=media_dict.get("file_size_bytes"),
            mime_type=media_dict.get("mime_type"),
            metadata=media_dict.get("metadata", {}),
        )

    @classmethod
    def normalize_content(
        cls,
        content_dict: Dict[str, Any],
        platform: str = "instagram",
    ) -> NormalizedContent:
        """Normalize platform content to a platform-neutral normalized object."""
        text = content_dict.get("text") or content_dict.get("caption") or ""
        hashtags = [tag.lstrip("#") for tag in re.findall(r"#([A-Za-z0-9_]+)", text)]
        mentions = [user.lstrip("@") for user in re.findall(r"@([A-Za-z0-9_]+)", text)]
        links = re.findall(r"https?://\S+", text)

        content_type = content_dict.get("content_type") or "post"
        return NormalizedContent(
            text=text,
            hashtags=hashtags,
            mentions=mentions,
            links=links,
            content_type=str(content_type),
            location=content_dict.get("location") or content_dict.get("location_id"),
            language=content_dict.get("language"),
            metadata={
                "platform": platform,
                "caption": content_dict.get("caption"),
                "raw_content": content_dict,
            },
        )

    @classmethod
    def denormalize_for_platform(
        cls,
        content: UniversalContent,
        platform: str,
    ) -> Dict[str, Any]:
        """Convert UniversalContent to platform-specific format."""
        if platform == "instagram":
            return cls._denormalize_instagram(content)
        elif platform == "twitter":
            return cls._denormalize_twitter(content)
        elif platform == "linkedin":
            return cls._denormalize_linkedin(content)
        elif platform == "facebook":
            return cls._denormalize_facebook(content)
        elif platform == "tiktok":
            return cls._denormalize_tiktok(content)
        else:
            return cls._denormalize_generic(content)

    @classmethod
    def _denormalize_instagram(cls, content: UniversalContent) -> Dict[str, Any]:
        """Convert to Instagram Graph API format."""
        media_type = cls._determine_instagram_media_type(content)

        result = {
            "media_type": media_type,
        }

        # Handle caption/text
        caption = content.caption or content.text
        if caption:
            result["caption"] = caption[:2200]

        # Handle media
        if content.media:
            if media_type == "CAROUSEL":
                result["children"] = [m.url for m in content.media]
            else:
                first_media = content.media[0]
                if first_media.type == MediaType.VIDEO or media_type in ("REELS", "VIDEO"):
                    result["video_url"] = first_media.url
                else:
                    result["image_url"] = first_media.url

                if first_media.thumbnail_url:
                    result["cover_url"] = first_media.thumbnail_url

        # Hashtags
        if content.hashtags:
            hashtags = " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])
            if result.get("caption"):
                result["caption"] += f"\n\n{hashtags}"
            else:
                result["caption"] = hashtags

        # Mentions (handled in caption)
        if content.mentions:
            mentions = " ".join([f"@{m.lstrip('@')}" for m in content.mentions[:20]])
            if result.get("caption"):
                result["caption"] += f" {mentions}"
            else:
                result["caption"] = mentions

        return result

    @classmethod
    def _denormalize_twitter(cls, content: UniversalContent) -> Dict[str, Any]:
        """Convert to Twitter API v2 format."""
        text_parts = []
        if content.text:
            text_parts.append(content.text)
        elif content.caption:
            text_parts.append(content.caption)

        if content.hashtags:
            text_parts.append(" ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:10]]))

        if content.mentions:
            text_parts.append(" ".join([f"@{m.lstrip('@')}" for m in content.mentions[:10]]))

        full_text = " ".join(text_parts)[:280]

        result = {
            "text": full_text,
        }

        if content.media:
            result["media"] = {
                "media_ids": [m.url for m in content.media[:4]],  # Twitter uses media IDs
            }

        return result

    @classmethod
    def _denormalize_linkedin(cls, content: UniversalContent) -> Dict[str, Any]:
        """Convert to LinkedIn API format."""
        text = content.text or content.caption or ""
        if content.hashtags:
            text += "\n\n" + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])

        return {
            "author": "urn:li:person:...",  # Would be filled by auth
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text[:3000]},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

    @classmethod
    def _denormalize_facebook(cls, content: UniversalContent) -> Dict[str, Any]:
        """Convert to Facebook Graph API format."""
        message = content.text or content.caption or ""
        if content.hashtags:
            message += "\n\n" + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:30]])

        result = {
            "message": message[:63206],
        }

        if content.media:
            if len(content.media) == 1:
                m = content.media[0]
                if m.type == MediaType.VIDEO:
                    result["video_url"] = m.url
                else:
                    result["url"] = m.url
            else:
                result["attached_media"] = [{"media_fbid": m.url} for m in content.media]

        return result

    @classmethod
    def _denormalize_tiktok(cls, content: UniversalContent) -> Dict[str, Any]:
        """Convert to TikTok API format."""
        caption = content.caption or content.text or ""
        if content.hashtags:
            caption += "\n" + " ".join([f"#{h.lstrip('#')}" for h in content.hashtags[:100]])

        return {
            "caption": caption[:2200],
            "video_url": content.media[0].url if content.media and content.media[0].type == MediaType.VIDEO else None,
        }

    @classmethod
    def _denormalize_generic(cls, content: UniversalContent) -> Dict[str, Any]:
        """Generic fallback denormalization."""
        return {
            "content_type": content.content_type.value,
            "text": content.text,
            "caption": content.caption,
            "hashtags": content.hashtags,
            "mentions": content.mentions,
            "media": [asdict(m) for m in content.media],
        }

    @classmethod
    def _determine_instagram_media_type(cls, content: UniversalContent) -> str:
        """Determine Instagram media type from content."""
        if content.content_type == ContentType.REEL:
            return "REELS"
        elif content.content_type == ContentType.STORY:
            return "STORIES"
        elif content.content_type == ContentType.CAROUSEL or len(content.media) > 1:
            return "CAROUSEL"
        elif content.media and content.media[0].type == MediaType.VIDEO:
            return "REELS"
        return "IMAGE"

    @classmethod
    def validate_for_platform(
        cls,
        content: UniversalContent,
        platform: str,
    ) -> List[str]:
        """Validate content against platform limits. Returns list of warnings."""
        warnings = []

        limits = cls.PLATFORM_LIMITS.get(platform, {})
        media_specs = cls.PLATFORM_MEDIA_SPECS.get(platform, {})

        # Check text/caption length
        text = content.caption or content.text or ""
        if "caption" in limits and len(text) > limits["caption"]:
            warnings.append(f"Caption exceeds {platform} limit of {limits['caption']} characters")

        # Check hashtags
        if "hashtags" in limits and len(content.hashtags) > limits["hashtags"]:
            warnings.append(f"Too many hashtags for {platform} (max {limits['hashtags']})")

        # Check mentions
        if "mentions" in limits and len(content.mentions) > limits["mentions"]:
            warnings.append(f"Too many mentions for {platform} (max {limits['mentions']})")

        # Check media
        for media in content.media:
            spec = media_specs.get(media.type.value, {})
            if "max_size_mb" in spec and media.file_size_bytes:
                max_bytes = spec["max_size_mb"] * 1024 * 1024
                if media.file_size_bytes > max_bytes:
                    warnings.append(f"Media {media.url} exceeds {platform} size limit of {spec['max_size_mb']}MB")

        return warnings