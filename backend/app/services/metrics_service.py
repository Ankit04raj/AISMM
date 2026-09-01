"""Metrics service - Business logic for analytics and insights."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import Post, PostPublication, SocialAccount, Metric, User
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import MetricNormalizer
from backend.app.core.schemas.insights import (
    PostInsights,
    AccountInsights,
    FollowerDemographics,
    MediaInsights,
)
from backend.app.core.errors import NotFoundError


class MetricsService:
    """Service for fetching and aggregating metrics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_post_insights(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> Optional[PostInsights]:
        """Get insights for a specific post."""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications))
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = result.scalar_one_or_none()
        if not post:
            return None

        all_metrics = {}
        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_post_id:
                try:
                    cached = await self._get_cached_metrics(
                        publication.platform,
                        publication.platform_post_id,
                        "post",
                    )
                    if cached:
                        all_metrics[publication.platform] = cached
                    else:
                        insights = await adapter.fetch_insights(publication.platform_post_id)
                        normalized = insights.get("normalized", {}) if isinstance(insights, dict) else {}
                        all_metrics[publication.platform] = normalized
                        await self._cache_metrics(
                            publication.platform,
                            publication.platform_post_id,
                            "post",
                            normalized,
                        )
                except Exception:
                    pass

        if not all_metrics:
            return None

        combined = self._combine_metrics(all_metrics)

        return PostInsights(
            post_id=str(post_id),
            platform=", ".join(all_metrics.keys()),
            impressions=combined.get("impressions"),
            reach=combined.get("reach"),
            likes=combined.get("likes"),
            comments=combined.get("comments"),
            shares=combined.get("shares"),
            saves=combined.get("saves"),
            video_views=combined.get("video_views"),
            engagement_rate=combined.get("engagement_rate"),
            fetched_at=datetime.now(timezone.utc),
        )

    async def get_account_insights(
        self,
        account_id: UUID,
        user_id: UUID,
    ) -> Optional[AccountInsights]:
        """Get insights for a social account."""
        result = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.id == account_id,
                    SocialAccount.user_id == user_id,
                )
            )
        )
        account = result.scalar_one_or_none()
        if not account or not account.is_active:
            return None

        adapter = PlatformRegistry.get_adapter(account.platform)
        if not adapter:
            return None

        try:
            cached = await self._get_cached_metrics(
                account.platform,
                account.platform_user_id,
                "account",
            )
            if cached:
                return AccountInsights(
                    platform=account.platform,
                    account_id=account.platform_user_id,
                    **cached,
                    fetched_at=datetime.now(timezone.utc),
                )

            insights = await adapter.fetch_account_insights()
            norm = insights.get("normalized", {}) if isinstance(insights, dict) else {}
            await self._cache_metrics(
                account.platform,
                account.platform_user_id,
                "account",
                norm,
            )

            return AccountInsights(
                platform=account.platform,
                account_id=account.platform_user_id,
                followers_count=norm.get("followers_count"),
                following_count=norm.get("following_count"),
                media_count=norm.get("media_count"),
                impressions=norm.get("impressions"),
                reach=norm.get("reach"),
                profile_views=norm.get("profile_views"),
                website_clicks=norm.get("clicks"),
                email_contacts=norm.get("email_contacts"),
                phone_call_clicks=norm.get("phone_call_clicks"),
                fetched_at=datetime.now(timezone.utc),
            )
        except Exception:
            return None

    async def get_user_overview(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get overview metrics for a user across all accounts."""
        accounts_res = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.user_id == user_id,
                    SocialAccount.is_active == True,
                )
            )
        )
        accounts = accounts_res.scalars().all()

        overview = {
            "total_accounts": len(accounts),
            "total_followers": 0,
            "total_impressions": 0,
            "total_engagements": 0,
            "total_posts": 0,
            "by_platform": {},
        }

        for account in accounts:
            adapter = PlatformRegistry.get_adapter(account.platform)
            if not adapter:
                continue

            try:
                insights = await adapter.fetch_account_insights()
                norm = insights.get("normalized", {}) if isinstance(insights, dict) else {}
                overview["by_platform"][account.platform] = norm

                overview["total_followers"] += norm.get("followers_count", 0)
                overview["total_impressions"] += norm.get("impressions", 0)
                overview["total_engagements"] += sum(
                    norm.get(k, 0)
                    for k in ["likes", "comments", "shares", "saves", "clicks"]
                )
            except Exception:
                pass

        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)
        post_count = await self.db.execute(
            select(func.count(Post.id)).where(
                and_(
                    Post.user_id == user_id,
                    Post.created_at >= cutoff,
                )
            )
        )
        overview["total_posts"] = post_count.scalar() or 0

        return overview

    async def get_top_posts(
        self,
        user_id: UUID,
        metric: str = "impressions",
        limit: int = 10,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get top performing posts for a user."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications))
            .where(
                and_(
                    Post.user_id == user_id,
                    Post.created_at >= cutoff,
                )
            )
        )
        posts = result.scalars().all()

        scored_posts = []
        for post in posts:
            total_metric = 0
            primary_platform = "unknown"
            for publication in post.publications:
                primary_platform = publication.platform
                adapter = PlatformRegistry.get_adapter(publication.platform)
                if adapter and publication.platform_post_id:
                    try:
                        insights = await adapter.fetch_insights(publication.platform_post_id)
                        norm = insights.get("normalized", {}) if isinstance(insights, dict) else {}
                        total_metric += norm.get(metric, 0)
                    except Exception:
                        pass

            if total_metric > 0:
                scored_posts.append({
                    "post_id": str(post.id),
                    "platform": primary_platform,
                    "content_type": post.content_type.value if hasattr(post.content_type, "value") else str(post.content_type),
                    "text": post.text[:100] if post.text else None,
                    "created_at": post.created_at.isoformat(),
                    "metric_value": total_metric,
                    "metric_name": metric,
                })

        scored_posts.sort(key=lambda x: x["metric_value"], reverse=True)
        return scored_posts[:limit]

    async def get_engagement_trends(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get engagement trends over time."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)
        result = await self.db.execute(
            select(Metric)
            .join(Post, Metric.post_id == Post.id)
            .where(
                and_(
                    Post.user_id == user_id,
                    Metric.fetched_at >= cutoff,
                )
            )
            .order_by(Metric.fetched_at.asc())
        )
        metrics = result.scalars().all()
        return [
            {
                "timestamp": m.fetched_at.isoformat(),
                "platform": m.platform,
                "metrics": m.metrics,
            }
            for m in metrics
        ]

    async def _get_cached_metrics(
        self,
        platform: str,
        entity_id: str,
        entity_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached metrics from database."""
        result = await self.db.execute(
            select(Metric)
            .where(
                and_(
                    Metric.platform == platform,
                    Metric.entity_id == entity_id,
                    Metric.entity_type == entity_type,
                )
            )
            .order_by(Metric.fetched_at.desc())
            .limit(1)
        )
        metric = result.scalar_one_or_none()
        if metric:
            return metric.metrics
        return None

    async def _cache_metrics(
        self,
        platform: str,
        entity_id: str,
        entity_type: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Cache metrics to database."""
        metric = Metric(
            platform=platform,
            entity_id=entity_id,
            entity_type=entity_type,
            metrics=metrics,
            fetched_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(metric)
        await self.db.commit()

    def _combine_metrics(self, all_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine metrics across multiple platforms."""
        combined = {
            "impressions": 0,
            "reach": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
            "video_views": 0,
            "clicks": 0,
        }
        for platform_metrics in all_metrics.values():
            for key in combined:
                combined[key] += platform_metrics.get(key, 0)

        total_interactions = sum([
            combined["likes"],
            combined["comments"],
            combined["shares"],
            combined["saves"],
        ])
        if combined["impressions"] > 0:
            combined["engagement_rate"] = round((total_interactions / combined["impressions"]) * 100, 2)
        else:
            combined["engagement_rate"] = 0.0

        return combined
