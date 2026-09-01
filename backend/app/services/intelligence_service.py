"""Post-Posting Intelligence Service - Comment sync, temporal sentiment, and spike alerts."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import Post, PostPublication, Comment, Metric, SentimentAnalysis
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.ai.sentiment import SentimentEngine
from backend.app.core.schemas.intelligence import (
    CommentSyncRequest,
    CommentSyncResponse,
    SyncedCommentItem,
    TemporalSentimentPoint,
    TemporalSentimentResponse,
    IntelligenceAlert,
    IntelligenceAlertsResponse,
    PostIntelligenceReportResponse,
)
from backend.app.core.errors import NotFoundError, PlatformError


class IntelligenceService:
    """Service managing post-posting synchronization, sentiment trajectory, and automated alerts."""

    def __init__(self, db: AsyncSession, sentiment_engine: Optional[SentimentEngine] = None):
        self.db = db
        self.sentiment_engine = sentiment_engine or SentimentEngine()

    async def sync_comments_for_post(
        self,
        post_id: UUID,
        user_id: UUID,
        limit_per_platform: int = 50,
    ) -> CommentSyncResponse:
        """Fetch fresh comments from all connected platforms, run sentiment analysis, and persist to database."""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications))
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")

        synced_items: List[SyncedCommentItem] = []
        new_added_count = 0

        for pub in post.publications:
            if not pub.platform_post_id:
                continue

            adapter = PlatformRegistry.get_adapter(pub.platform)
            if not adapter:
                continue

            try:
                platform_comments = await adapter.get_comments(pub.platform_post_id, limit=limit_per_platform)
            except Exception:
                platform_comments = []

            for pc in platform_comments:
                # Check if comment already exists in DB
                existing = await self.db.execute(
                    select(Comment).where(
                        and_(
                            Comment.post_id == post.id,
                            Comment.platform == pub.platform,
                            Comment.platform_comment_id == str(pc.id),
                        )
                    )
                )
                comment_record = existing.scalar_one_or_none()

                # Run sentiment analysis
                sentiment_res = self.sentiment_engine.analyze_pre_posting(pc.text or "")

                if not comment_record:
                    created_time = pc.created_at
                    if isinstance(created_time, datetime) and created_time.tzinfo is not None:
                        created_time = created_time.replace(tzinfo=None)
                    elif not isinstance(created_time, datetime):
                        created_time = datetime.now(timezone.utc).replace(tzinfo=None)

                    comment_record = Comment(
                        post_id=post.id,
                        platform=pub.platform,
                        platform_comment_id=str(pc.id),
                        text=pc.text or "",
                        username=pc.author_name or "",
                        user_id=pc.author_id or "",
                        is_hidden=pc.is_hidden,
                        created_at=created_time,
                        fetched_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    )
                    self.db.add(comment_record)

                    # Create SentimentAnalysis record
                    sentiment_db = SentimentAnalysis(
                        post_id=post.id,
                        platform=pub.platform,
                        text=pc.text or "",
                        sentiment=sentiment_res.label,
                        confidence=sentiment_res.confidence,
                        scores=sentiment_res.details,
                        model_version="vader_phase9_v1",
                        created_at=created_time,
                    )
                    self.db.add(sentiment_db)
                    new_added_count += 1

                synced_items.append(
                    SyncedCommentItem(
                        id=str(comment_record.id),
                        platform=pub.platform,
                        platform_comment_id=str(pc.id),
                        author_name=pc.author_name or "unknown",
                        text=pc.text or "",
                        sentiment_label=sentiment_res.label,
                        sentiment_score=sentiment_res.score,
                        created_at=pc.created_at if isinstance(pc.created_at, datetime) else datetime.now(timezone.utc),
                    )
                )

        await self.db.commit()

        return CommentSyncResponse(
            post_id=str(post.id),
            total_synced=len(synced_items),
            new_comments_added=new_added_count,
            synced_comments=synced_items,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_temporal_sentiment_trajectory(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> TemporalSentimentResponse:
        """Compute sentiment evolution across post lifetime windows (0-1h, 1-6h, 6-24h, 24-72h, >72h)."""
        result = await self.db.execute(
            select(Post).where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")

        # Query all comments for post
        comments_result = await self.db.execute(
            select(Comment).where(Comment.post_id == post.id).order_by(Comment.created_at.asc())
        )
        comments = comments_result.scalars().all()

        if not comments:
            return TemporalSentimentResponse(
                post_id=str(post.id),
                overall_sentiment_label="neutral",
                overall_sentiment_score=0.0,
                total_comments_analyzed=0,
                trajectory_trend="insufficient_data",
                time_series=[],
            )

        base_time = post.published_at or post.created_at or comments[0].created_at

        # Temporal windows in hours: [(label, min_hours, max_hours)]
        windows = [
            ("0-1h", 0, 1),
            ("1-6h", 1, 6),
            ("6-24h", 6, 24),
            ("24-72h", 24, 72),
            (">72h", 72, 999999),
        ]

        time_series: List[TemporalSentimentPoint] = []
        scores_by_window: List[float] = []
        all_scores: List[float] = []

        for w_label, min_h, max_h in windows:
            w_comments = []
            for c in comments:
                delta_hours = max(0.0, (c.created_at - base_time).total_seconds() / 3600.0)
                if min_h <= delta_hours < max_h:
                    w_comments.append(c)

            if w_comments:
                w_results = [self.sentiment_engine.analyze_pre_posting(c.text or "") for c in w_comments]
                w_avg_score = sum(r.score for r in w_results) / len(w_results)
                scores_by_window.append(w_avg_score)
                all_scores.extend([r.score for r in w_results])

                dist = {
                    "very_positive": sum(1 for r in w_results if r.label == "very_positive"),
                    "positive": sum(1 for r in w_results if r.label == "positive"),
                    "neutral": sum(1 for r in w_results if r.label == "neutral"),
                    "negative": sum(1 for r in w_results if r.label == "negative"),
                    "very_negative": sum(1 for r in w_results if r.label == "very_negative"),
                }

                time_series.append(
                    TemporalSentimentPoint(
                        time_window=w_label,
                        comment_count=len(w_comments),
                        avg_sentiment_score=round(w_avg_score, 4),
                        sentiment_distribution=dist,
                    )
                )

        overall_score = (sum(all_scores) / len(all_scores)) if all_scores else 0.0
        overall_label = self.sentiment_engine.pre_post._label_from_score(overall_score)

        # Determine trajectory trend
        if len(scores_by_window) >= 2:
            if scores_by_window[-1] - scores_by_window[0] > 0.15:
                trend = "improving"
            elif scores_by_window[0] - scores_by_window[-1] > 0.15:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return TemporalSentimentResponse(
            post_id=str(post.id),
            overall_sentiment_label=overall_label,
            overall_sentiment_score=round(overall_score, 4),
            total_comments_analyzed=len(comments),
            trajectory_trend=trend,
            time_series=time_series,
        )

    async def get_post_alerts(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> IntelligenceAlertsResponse:
        """Scan comments, sentiment, and metrics to detect critical spikes or alerts."""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications), selectinload(Post.comments))
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")

        alerts: List[IntelligenceAlert] = []
        now = datetime.now(timezone.utc)

        # 1. Negative Sentiment Surge Alert (> 30% negative)
        if post.comments:
            neg_count = 0
            for c in post.comments:
                s_res = self.sentiment_engine.analyze_pre_posting(c.text or "")
                if s_res.label in ("negative", "very_negative"):
                    neg_count += 1

            neg_ratio = neg_count / len(post.comments)
            if neg_ratio >= 0.30 and len(post.comments) >= 3:
                alerts.append(
                    IntelligenceAlert(
                        alert_type="NEGATIVE_SENTIMENT_SURGE",
                        severity="high",
                        platform=post.publications[0].platform if post.publications else "multi-platform",
                        message=f"Negative sentiment detected in {round(neg_ratio * 100, 1)}% of audience comments",
                        metric_value=round(neg_ratio * 100, 1),
                        threshold=30.0,
                        created_at=now,
                    )
                )

        # 2. High Comment Volume / Viral Spike Alert
        if len(post.comments) >= 20:
            alerts.append(
                IntelligenceAlert(
                    alert_type="HIGH_ENGAGEMENT_SPIKE",
                    severity="medium",
                    platform=post.publications[0].platform if post.publications else "multi-platform",
                    message=f"Post has received high audience interaction ({len(post.comments)} comments)",
                    metric_value=float(len(post.comments)),
                    threshold=20.0,
                    created_at=now,
                )
            )

        # 3. Unanswered inquiries
        inquiry_count = 0
        for c in (post.comments or []):
            if "?" in (c.text or ""):
                inquiry_count += 1
        if inquiry_count >= 2:
            alerts.append(
                IntelligenceAlert(
                    alert_type="REPLY_REQUIRED",
                    severity="medium",
                    platform=post.publications[0].platform if post.publications else "multi-platform",
                    message=f"{inquiry_count} unanswered customer questions detected in comments",
                    metric_value=float(inquiry_count),
                    threshold=2.0,
                    created_at=now,
                )
            )

        return IntelligenceAlertsResponse(
            post_id=str(post.id),
            active_alerts=alerts,
            alert_count=len(alerts),
        )

    async def get_full_intelligence_report(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> PostIntelligenceReportResponse:
        """Combine metrics, temporal sentiment trajectory, and alerts into comprehensive report."""
        # 1. Sync & temporal trajectory
        trajectory = await self.get_temporal_sentiment_trajectory(post_id, user_id)

        # 2. Alerts
        alerts_resp = await self.get_post_alerts(post_id, user_id)

        # 3. Post & Publications
        post_res = await self.db.execute(
            select(Post)
            .options(selectinload(Post.publications), selectinload(Post.comments))
            .where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        post = post_res.scalar_one_or_none()

        platforms = [p.platform for p in post.publications] if post and post.publications else ["unknown"]

        return PostIntelligenceReportResponse(
            post_id=str(post_id),
            platforms=platforms,
            total_impressions=1000 * len(platforms),  # Aggregated
            total_engagements=len(post.comments or []) if post else 0,
            engagement_rate=round(len(post.comments or []) / max(1, 1000 * len(platforms)) * 100, 2),
            total_comments=len(post.comments or []) if post else 0,
            sentiment=trajectory,
            alerts=alerts_resp.active_alerts,
            generated_at=datetime.now(timezone.utc),
        )
