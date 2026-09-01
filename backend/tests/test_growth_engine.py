"""Tests for Phase 11 Predictive Growth Engine (Random Forest Regressors, Feature Pipeline, API, Service)."""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.growth import GrowthEngine, GrowthFeatureExtractor
from backend.app.services.growth_service import GrowthService
from backend.app.core.schemas.growth import GrowthPredictRequest
from backend.app.db.models import SocialAccount, Post, ModelPrediction

client = TestClient(app)


class TestGrowthFeatureExtractor:
    """Test feature extraction for growth modeling."""

    def test_feature_extraction_vector(self):
        feat = GrowthFeatureExtractor.extract(
            platform="instagram",
            current_followers=10000,
            following_count=500,
            posts_last_30_days=15,
            avg_engagement_rate=4.8,
            followers_gained_7d=120,
            followers_gained_30d=480,
            video_count=6,
            carousel_count=5,
            total_posts=15,
            avg_sentiment_score=0.45,
        )

        assert feat.current_followers == 10000
        assert feat.posting_frequency_weekly == 3.5
        assert feat.avg_engagement_rate == 4.8
        assert feat.video_ratio == 0.4
        assert feat.carousel_ratio == 0.33
        assert len(feat.to_vector()) == 10


class TestGrowthEngine:
    """Test machine learning regression predictions and research baselines."""

    def test_engine_initialization_and_r2_baselines(self):
        engine = GrowthEngine()
        assert "instagram" in engine.models
        assert "facebook" in engine.models
        assert "twitter" in engine.models

        # Verify research R2 targets are tracked and calibrated
        ig_metrics = engine.metrics["instagram"]
        assert ig_metrics["target_baseline_r2"] == 0.892
        assert ig_metrics["r2"] >= 0.85
        assert ig_metrics["rmse"] > 0

    def test_multi_horizon_predictions(self):
        engine = GrowthEngine()
        result = engine.predict_growth(
            platform="instagram",
            current_followers=5000,
            posting_frequency_weekly=4.0,
            avg_engagement_rate=5.2,
        )

        assert result.platform == "instagram"
        assert result.current_followers == 5000
        assert "7d" in result.projections
        assert "30d" in result.projections
        assert "90d" in result.projections

        # Projections should be monotonically increasing
        p7 = result.projections["7d"]
        p30 = result.projections["30d"]
        p90 = result.projections["90d"]

        assert p7.predicted_followers > 5000
        assert p30.predicted_followers > p7.predicted_followers
        assert p90.predicted_followers > p30.predicted_followers
        assert p30.confidence_r2 >= 0.85
        assert len(result.feature_importances) == 10


class TestGrowthService:
    """Test GrowthService database persistence and workflows."""

    @pytest.mark.asyncio
    async def test_predict_and_account_projection(self):
        mock_db = AsyncMock()
        service = GrowthService(mock_db)

        # 1. Direct prediction
        req = GrowthPredictRequest(
            platform="instagram",
            current_followers=8000,
            posting_frequency_weekly=3.5,
            avg_engagement_rate=4.5,
        )
        res = await service.predict_growth(req)
        assert res.platform == "instagram"
        assert res.projections["30d"].predicted_followers > 8000

        # 2. Account-linked projection
        user_id = uuid4()
        account_id = uuid4()

        mock_account = MagicMock(spec=SocialAccount)
        mock_account.id = account_id
        mock_account.user_id = user_id
        mock_account.platform = "instagram"
        mock_account.username = "brand_growth_hub"
        mock_account.account_metadata = {"followers_count": 12000}

        mock_db_acc = MagicMock()
        mock_db_acc.scalar_one_or_none.return_value = mock_account

        mock_db_posts = MagicMock()
        mock_db_posts.scalar.return_value = 10

        mock_db.execute.side_effect = [mock_db_acc, mock_db_posts]

        acc_res = await service.get_account_projections(account_id, user_id)
        assert acc_res.username == "brand_growth_hub"
        assert acc_res.current_followers == 12000
        assert acc_res.projections["30d"].predicted_followers > 12000
        assert mock_db.add.called
        assert mock_db.commit.called


class TestGrowthAPIEndpoints:
    """Test FastAPI /api/v1/growth endpoints."""

    def test_predict_endpoint(self):
        resp = client.post(
            "/api/v1/growth/predict",
            json={
                "platform": "instagram",
                "current_followers": 15000,
                "posting_frequency_weekly": 4.0,
                "avg_engagement_rate": 5.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"
        assert "30d" in data["projections"]
        assert data["projections"]["30d"]["predicted_followers"] > 15000
        assert data["baseline_r2"] == 0.892

    def test_models_status_endpoint(self):
        resp = client.get("/api/v1/growth/models/status")
        assert resp.status_code == 200
        models = resp.json()
        assert len(models) >= 3
        platforms = [m["platform"] for m in models]
        assert "instagram" in platforms
        assert "facebook" in platforms
        assert "twitter" in platforms
        assert models[0]["r2_score"] > 0.80
