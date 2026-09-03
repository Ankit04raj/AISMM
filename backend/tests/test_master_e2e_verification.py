"""Phase 17 Master End-to-End System Verification Suite.

Validates the complete unified AISMM ecosystem across all 5 social platforms
(Instagram, Facebook, X, LinkedIn, YouTube) and all 8 AI engines.
"""

import pytest
import time
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.platform_adapters.base import PlatformCapability
from backend.app.core.normalization import (
    UniversalContent,
    UniversalMedia,
    ContentType,
    MediaType,
    MetricNormalizer,
)
from backend.app.core.vault import SecretVault
from backend.app.core.rate_limit import SlidingWindowRateLimiter
from backend.app.core.resilience import CircuitBreaker, CircuitState, async_retry_with_backoff
from backend.app.core.audit import AuditLogger, AuditEventType
from backend.app.ai.sentiment.engine import SentimentEngine
from backend.app.ai.caption.engine import CaptionEngine
from backend.app.ai.hashtag.engine import HashtagEngine
from backend.app.ai.scheduling.engine import SchedulingEngine
from backend.app.ai.reply.engine import TFIDFReplyEngine, ReplyAction
from backend.app.ai.growth.engine import GrowthEngine
from backend.app.ai.strategy.engine import AIStrategyEngine
from backend.app.ai.evaluation.evaluator import ModelEvaluator
from backend.app.ai.registry.model_registry import ModelRegistryManager, ModelStage


class TestMasterEndToEndVerification:
    """Complete multi-platform, multi-model end-to-end integration and verification."""

    @pytest.fixture
    def user_id(self):
        return uuid4()

    def test_01_platform_registry_and_capability_discovery(self):
        """Verify all 5 platforms are registered and capability discovery works."""
        platforms = PlatformRegistry.list_platforms()
        assert "instagram" in platforms
        assert "facebook" in platforms
        assert "x" in platforms
        assert "twitter" in platforms
        assert "linkedin" in platforms
        assert "youtube" in platforms

        for p in ["instagram", "facebook", "x", "linkedin", "youtube"]:
            adapter = PlatformRegistry.get_adapter(p, config={"client_id": "test", "client_secret": "test"})
            assert adapter is not None
            assert adapter.platform_name in (p, "x" if p == "twitter" else p)

    def test_02_secret_vault_and_security_at_rest(self):
        """Verify AES-256 Vault encryption protects OAuth tokens and secrets."""
        vault = SecretVault(master_key="aismm_e2e_master_verification_key")
        tokens = {
            "access_token": "live_oauth_access_token_1234567890",
            "refresh_token": "live_oauth_refresh_token_0987654321",
            "client_secret": "super_secret_client_key",
            "platform": "instagram",
        }
        encrypted = vault.encrypt_dict(tokens)
        assert encrypted["access_token"] != tokens["access_token"]
        assert encrypted["refresh_token"] != tokens["refresh_token"]
        assert encrypted["platform"] == "instagram"

        decrypted = vault.decrypt_dict(encrypted)
        assert decrypted == tokens

    def test_03_ai_content_engine_pre_posting_optimization(self):
        """Verify AI content optimization (Sentiment + Caption Quality + Top-K Hashtags)."""
        raw_draft = "Excited to launch our new AI-powered platform for creator growth and analytics! Check it out!"

        # 1. Dual-phase pre-posting sentiment
        sent_engine = SentimentEngine()
        sent_res = sent_engine.analyze_pre_posting(raw_draft)
        assert sent_res.label in ("positive", "very_positive")
        assert sent_res.score > 0.3

        # 2. Caption quality index scoring
        caption_engine = CaptionEngine()
        cap_analysis = caption_engine.analyze(raw_draft, platform="instagram")
        assert cap_analysis.score > 60
        assert cap_analysis.features.word_count > 5

        # 3. Platform caption optimization
        ig_caption = caption_engine.optimize_for_platform(raw_draft, platform="instagram")
        tw_caption = caption_engine.optimize_for_platform(raw_draft, platform="twitter")
        li_caption = caption_engine.optimize_for_platform(raw_draft, platform="linkedin")
        assert len(ig_caption) > 0
        assert len(tw_caption) <= 280
        assert len(li_caption) > 0

        # 4. Top-K Hashtag recommendations
        tag_engine = HashtagEngine()
        tags_res = tag_engine.recommend_hashtags(raw_draft, platform="instagram", top_k=5)
        assert len(tags_res.top_k) > 0

    def test_04_intelligent_scheduling_ensemble(self):
        """Verify ML ensemble predicts high-engagement time slots across platforms."""
        sched_engine = SchedulingEngine()
        res_ig = sched_engine.recommend_best_times("instagram", text="AI Announcement", hashtags=["#ai", "#tech"], top_k=3)
        res_li = sched_engine.recommend_best_times("linkedin", text="AI Announcement", hashtags=["#leadership"], top_k=3)

        assert len(res_ig.recommendations) == 3
        assert len(res_li.recommendations) == 3
        assert res_ig.baseline_accuracy == 88.08
        assert res_ig.recommendations[0].predicted_engagement_score > 0

    @pytest.mark.asyncio
    async def test_05_multi_platform_publishing_workflow(self):
        """Verify publishing normalized content across Instagram, Facebook, X, LinkedIn, YouTube."""
        content = UniversalContent(
            content_type=ContentType.POST,
            text="Autonomous multi-platform publishing verified by AISMM.",
            caption="Autonomous multi-platform publishing verified by AISMM.",
            hashtags=["AISMM", "Innovation"],
            media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/asset.jpg")],
        )

        # 1. Instagram
        ig_adapter = PlatformRegistry.get_adapter("instagram", config={"access_token": "ig_token", "instagram_business_account_id": "ig_123"})
        with patch.object(ig_adapter, "_get_client") as mock_ig:
            mock_ig.return_value.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {"id": "ig_media_101"}))
            mock_ig.return_value.get = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {"status_code": "FINISHED", "id": "ig_media_101"}))
            # Instagram publisher flow
            ig_pub = await ig_adapter.publish_post(content)
            assert ig_pub.platform_post_id == "ig_media_101"

        # 2. Facebook
        fb_adapter = PlatformRegistry.get_adapter("facebook", config={"access_token": "fb_token", "page_id": "fb_123"})
        with patch.object(fb_adapter, "_get_client") as mock_fb:
            mock_fb.return_value.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {"id": "fb_102", "post_id": "fb_post_102"}))
            fb_pub = await fb_adapter.publish_post(content)
            assert fb_pub.platform_post_id == "fb_post_102"

        # 3. X (Twitter)
        x_adapter = PlatformRegistry.get_adapter("x", config={"access_token": "x_token", "account_username": "aismm"})
        with patch.object(x_adapter, "_get_client") as mock_x:
            mock_x.return_value.post = AsyncMock(return_value=MagicMock(status_code=201, json=lambda: {"data": {"id": "x_tweet_103"}}))
            x_pub = await x_adapter.publish_post(content)
            assert x_pub.platform_post_id == "x_tweet_103"

        # 4. LinkedIn
        li_adapter = PlatformRegistry.get_adapter("linkedin", config={"access_token": "li_token", "organization_urn": "urn:li:organization:104"})
        with patch.object(li_adapter, "_get_client") as mock_li:
            mock_li.return_value.post = AsyncMock(return_value=MagicMock(status_code=201, json=lambda: {"id": "urn:li:ugcPost:104"}))
            li_pub = await li_adapter.publish_post(content)
            assert li_pub.platform_post_id == "urn:li:ugcPost:104"

        # 5. YouTube
        yt_content = UniversalContent(
            content_type=ContentType.VIDEO,
            text="YouTube video test",
            caption="YouTube video test",
            media=[UniversalMedia(type=MediaType.VIDEO, url="https://example.com/demo.mp4")],
        )
        yt_adapter = PlatformRegistry.get_adapter("youtube", config={"access_token": "yt_token", "channel_id": "yt_105"})
        with patch.object(yt_adapter, "_get_client") as mock_yt:
            mock_yt.return_value.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {"id": "yt_vid_105", "snippet": {"title": "Demo"}}))
            yt_pub = await yt_adapter.publish_post(yt_content)
            assert yt_pub.platform_post_id == "yt_vid_105"

    def test_06_auto_reply_intent_classification_and_routing(self):
        """Verify TF-IDF Auto-Reply engine and Human-in-the-Loop policy actions."""
        reply_engine = TFIDFReplyEngine()

        # Pricing inquiry -> High confidence -> Automatic / Approval
        p_res = reply_engine.generate_reply("What are your monthly subscription prices?", comment_id="c_001")
        assert p_res.intent.value == "pricing_inquiry"
        assert p_res.confidence >= 0.70
        assert p_res.suggested_reply is not None
        assert p_res.routing_action in (ReplyAction.AUTOMATIC, ReplyAction.APPROVAL_REQUIRED)

        # Praise compliment
        c_res = reply_engine.generate_reply("Love the new features, amazing work!", comment_id="c_002")
        assert c_res.intent.value == "compliment_praise"
        assert len(c_res.suggested_reply) > 0

        # Spam troll
        s_res = reply_engine.generate_reply("FREE CRYPTO COINS CLICK HERE NOW http://spam.xyz", comment_id="c_003")
        assert s_res.routing_action == ReplyAction.IGNORE_SPAM

    def test_07_predictive_growth_multi_horizon_forecasting(self):
        """Verify Random Forest Growth Regressors across horizons."""
        growth_engine = GrowthEngine()
        result = growth_engine.predict_growth(
            platform="instagram",
            current_followers=10000,
            posting_frequency_weekly=4.0,
            avg_engagement_rate=4.8,
        )
        assert result.platform == "instagram"
        assert result.baseline_r2 == 0.892
        assert "7d" in result.projections
        assert "30d" in result.projections
        assert "90d" in result.projections
        assert result.projections["30d"].predicted_followers > 10000
        assert result.projections["30d"].predicted_reach > 0

    def test_08_ai_strategy_engine_multi_model_synthesis(self):
        """Verify master AI Strategy Engine synthesizes multi-model recommendations."""
        strategy_engine = AIStrategyEngine()
        strategy = strategy_engine.generate_comprehensive_strategy(
            connected_platforms=["instagram", "facebook", "x", "linkedin"],
            recent_sentiment_score=0.55,
            average_engagement_rate=4.5,
            posting_frequency_weekly=3.5,
            total_followers=25000,
        )

        assert len(strategy.active_recommendations) >= 3
        assert len(strategy.platform_profiles) == 4
        assert strategy.overall_strategy_health_score > 60

        # Plan generation for a draft
        plan = strategy_engine.synthesize_content_strategy(
            draft_caption="Building future autonomous AI systems!",
            target_platforms=["instagram", "linkedin"],
            media_type="carousel",
            content_category="tech",
        )
        assert "instagram" in plan.optimized_caption_by_platform
        assert "linkedin" in plan.optimized_caption_by_platform
        assert len(plan.recommended_hashtags) > 0
        assert plan.projected_engagement_rate > 0

    def test_09_model_evaluation_and_registry_audit(self):
        """Verify ModelEvaluator evaluates all models live and manages cataloging."""
        evaluator = ModelEvaluator()
        audit = evaluator.evaluate_all_models()
        assert audit.total_registered_models == 6
        assert len(audit.models) == 6
        assert audit.system_average_latency_ms < 50.0

        registry = ModelRegistryManager()
        models = registry.list_models()
        assert len(models) == 6
        assert all(m.is_production for m in models)

    def test_10_production_hardening_resilience_and_audit(self):
        """Verify RateLimiter, CircuitBreaker, and AuditLogger work as one system."""
        # Rate Limiting
        limiter = SlidingWindowRateLimiter()
        for _ in range(5):
            limited, _, _ = limiter.is_rate_limited("client_ip_1", max_requests=5, window_seconds=10)
            assert limited is False
        limited, _, _ = limiter.is_rate_limited("client_ip_1", max_requests=5, window_seconds=10)
        assert limited is True

        # Circuit Breaker
        cb = CircuitBreaker("test_api", failure_threshold=2, recovery_timeout_seconds=0.1)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

        # Audit Logger
        logger = AuditLogger()
        event = logger.log_event(
            event_type=AuditEventType.POST_PUBLISHED,
            user_id="user_master_e2e",
            action="Master E2E Verification Complete",
            target_resource="aismm_system",
            status="SUCCESS",
        )
        assert event.event_type == AuditEventType.POST_PUBLISHED
        assert event.status == "SUCCESS"
