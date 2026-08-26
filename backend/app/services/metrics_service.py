"""Metrics service - Business logic for analytics and insights."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import Post, PostPublication, SocialAccount, Metric, User
from backend.app.core.platform_adapters import PlatformRegistry
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
        # Get post with publications
        result = await self.db.execute(
            select(Post).
            options(selectinload(Post.publications)).
            where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = result.scalar_one_or_none()
        if not post:
            return None

        all_metrics = {}
        for publication in post.publications:
            adapter = PlatformRegistry.get_adapter(publication.platform)
            if adapter and publication.platform_post_id:
                try:
                    # Try to get from cached metrics first
                    cached = await self._get_cached_metrics(
                        publication.platform,
                        publication.platform_post_id,
                        "post"
                    )
                    if cached:
                        all_metrics[publication.platform] = cached
                    else:
                        # Fetch from platform
                        insights = await adapter.fetch_insights(
                            publication.platform_post_id,
                            account_access_token=None,  # Would need token from account
                        )
                        all_metrics[publication.platform] = insights
                        # Cache for future
                        await self._cache_metrics(
                            publication.platform,
                            publication.platform_post_id,
                            "post",
                            insights,
                        )
                except Exception:
                    pass

        if not all_metrics:
            return None

        # Combine metrics
        combined = self._combine_metrics(all_metrics)

        return PostInsights(
            post_id=str(post_id),
            platform=", ".join(all_metrics.keys()),
            **combined,
            fetched_at=datetime.utcnow(),
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
            # Get cached or fetch fresh
            cached = await self._get_cached_metrics(
                account.platform,
                account.platform_user_id,
                "account"
            )
            if cached:
                return AccountInsights(
                    platform=account.platform,
                    account_id=account.platform_user_id,
                    **cached,
                    fetched_at=datetime.utcnow(),
                )

            insights = await adapter.fetch_account_insights(account.access_token)
            await self._cache_metrics(
                account.platform,
                account.platform_user_id,
                "account",
                insights,
            )

            return AccountInsights(
                platform=account.platform,
                account_id=account.platform_user_id,
                **insights,
                fetched_at=datetime.utcnow(),
            )
        except Exception:
            return None

    async def get_user_overview(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get overview metrics for a user across all accounts."""
        accounts = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.user_id == user_id,
                    SocialAccount.is_active == True,
                )
            )
        )
        accounts = accounts.scalars().all()

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
                insights = await adapter.fetch_account_insights(account.access_token)
                overview["by_platform"][account.platform] = insights

                overview["total_followers"] += insights.get("followers_count", 0)
                overview["total_impressions"] += insights.get("impressions", 0)
                overview["total_engagements"] += sum(
                    insights.get(k, 0)
                    for k in ["likes", "comments", "shares", "saves"]
                )
            except Exception:
                pass

        # Get post count
        post_count = await self.db.execute(
            select(func.count(Post.id)).where(
                and_(
                    Post.user_id == user_id,
                    Post.created_at >= datetime.utcnow() - timedelta(days=days),
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
        result = await self.db.execute(
            select(Post).
            options(selectinload(Post.publications)).
            where(
                and_(
                    Post.user_id == user_id,
                    Post.created_at >= datetime.utcnow() - timedelta(days=days),
                )
            )
        )
        posts = result.scalars().all()

        scored_posts = []
        for post in posts:
            # Get metrics from platforms
            total_metric = 0
            for publication in post.publications:
                adapter = PlatformRegistry.get_adapter(publication.platform)
                if adapter and publication.platform_post_id:
                    try:
                        insights = await adapter.fetch_insights(publication.platform_post_id)
                        total_metric += insights.get(metric, 0)
                    except Exception:
                        pass

            if total_metric > 0:
                scored_posts.append({
                    "post_id": str(post.id),
                    "platform": publication.platform,
                    "content_type": post.content_type,
                    "text": post.text[:100] if post.text else None,
                    "created_at": post.created_at.isoformat(),
                    "metric_value": total_metric,
                    "metric_name": metric,
                })

        # Sort by metric descending
        scored_posts.sort(key=lambda x: x["metric_value"], reverse=True)
        return scored_posts[:limit]

    async def get_engagement_trends(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get engagement trends over time."""
        # This would typically query the metrics table
        # For now, return empty - would need historical metrics storage
        return []

    async def _get_cached_metrics(
        self,
        platform: str,
        entity_id: str,
        entity_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached metrics from database."""
        result = await self.db.execute(
            select(Metric).where(
                and_(
                    Metric.platform == platform,
                    Metric.entity_id == entity_id,
                    Metric.entity_type == entity_type,
                )
            ).order_by(Metric.fetched_at.desc()).limit(1)
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
            fetched_at=datetime.utcnow(),
        )
        self.db.add(metric)
        await self.db.commit()

    def _combine_metrics(self, all_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine metrics from multiple platforms."""
        combined = {}
        for platform_metrics in all_metrics.values():
            for key, value in platform_metrics.items():
                if isinstance(value, (int, float)):
                    combined[key] = combined.get(key, 0) + value
        return combined