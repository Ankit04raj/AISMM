"""Comprehensive test suite for Phase 15 Model Improvement, Evaluation, and Registry with Honest Holdout Splits."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sklearn.metrics import r2_score, accuracy_score, f1_score

from backend.app.main import app
from backend.app.ai.evaluation.evaluator import ModelEvaluator
from backend.app.ai.registry.model_registry import ModelRegistryManager
from backend.app.ai.growth.engine import GrowthEngine
from backend.app.ai.scheduling.engine import SchedulingEngine
from backend.app.ai.reply.engine import TFIDFReplyEngine
from backend.app.services.model_service import ModelService
from backend.app.core.schemas.model_eval import (
    ModelStage,
    SingleModelEvaluationReport,
    FeatureImportanceItem,
    ClassImbalanceItem,
    ConfusionMatrixData,
    ModelDriftReport,
    ComprehensiveModelAuditResponse,
    ModelPromotionRequest,
)

client = TestClient(app)


class TestModelEvaluator:
    """Test ModelEvaluator diagnostic metrics and research baseline validations."""

    @pytest.fixture
    def evaluator(self):
        return ModelEvaluator()

    def test_evaluate_scheduling_engine(self, evaluator):
        report = evaluator.evaluate_scheduling_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "scheduling"
        assert report.accuracy > 0
        assert report.accuracy == evaluator.scheduling_engine.evaluate_on_heldout()["accuracy"]
        assert len(report.feature_importances) >= 4
        assert report.latency_ms < 200.0

    def test_evaluate_sentiment_engine(self, evaluator):
        report = evaluator.evaluate_sentiment_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "sentiment"
        assert report.accuracy > 0
        assert report.confusion_matrix is not None
        assert len(report.confusion_matrix.labels) == 3
        assert report.latency_ms < 30.0

    def test_evaluate_auto_reply_engine_with_class_balance(self, evaluator):
        report = evaluator.evaluate_auto_reply_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "auto_reply"
        assert report.accuracy > 0
        assert report.accuracy == evaluator.reply_engine.evaluate_on_heldout()["accuracy"]
        assert len(report.class_balance) == 6

    def test_evaluate_growth_engine(self, evaluator):
        report = evaluator.evaluate_growth_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "growth"
        assert report.r2_score > 0
        assert report.r2_score == evaluator.growth_engine.evaluate_on_heldout("instagram")["r2"]
        assert report.rmse is not None
        assert len(report.feature_importances) >= 5

    def test_evaluate_hashtag_engine(self, evaluator):
        report = evaluator.evaluate_hashtag_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "hashtag"
        assert report.top_k_accuracy > 0
        assert "Rule-based" in report.framework

    def test_evaluate_caption_engine(self, evaluator):
        report = evaluator.evaluate_caption_engine()
        assert isinstance(report, SingleModelEvaluationReport)
        assert report.task == "caption"
        assert report.accuracy > 0
        assert len(report.feature_importances) == 4
        assert "Rule-based" in report.framework

    def test_evaluate_all_models(self, evaluator):
        audit = evaluator.evaluate_all_models()
        assert isinstance(audit, ComprehensiveModelAuditResponse)
        assert audit.total_registered_models == 6
        assert audit.production_models_count == 6
        assert audit.system_average_latency_ms < 50.0

    def test_detect_model_drift_calibrated(self, evaluator):
        drift = evaluator.detect_model_drift("scheduling", current_metric_value=88.20)
        assert isinstance(drift, ModelDriftReport)
        assert drift.drift_detected is False
        assert drift.retraining_recommended is False

    def test_detect_model_drift_severe(self, evaluator):
        drift = evaluator.detect_model_drift("scheduling", current_metric_value=70.00)
        assert isinstance(drift, ModelDriftReport)
        assert drift.drift_detected is True
        assert drift.retraining_recommended is True
        assert len(drift.diagnostics) > 0


class TestHonestMLHoldoutValidationProof:
    """Proof for Section 5: ML engines train on designated split, evaluate on held-out split, and metrics match independent recomputation."""

    def test_growth_engine_heldout_reproducible_evaluation(self):
        """Growth engine R2 on held-out test split matches independent recomputation."""
        engine = GrowthEngine()
        metrics = engine.evaluate_on_heldout("instagram")

        # Independent recomputation on the exact held-out test split
        X_test, y_test = engine.heldout_test_data["instagram"]
        y_pred = engine.models["instagram"].predict(X_test)
        independent_r2 = round(float(r2_score(y_test, y_pred)), 4)

        assert metrics["r2"] == independent_r2, (
            f"Reported R2 {metrics['r2']} does not match independent recomputation {independent_r2}"
        )
        assert metrics["r2"] > 0.70

    def test_scheduling_engine_heldout_reproducible_evaluation(self):
        """Scheduling ensemble accuracy on held-out test split matches independent recomputation."""
        engine = SchedulingEngine()
        metrics = engine.evaluate_on_heldout()

        # Independent recomputation on the exact held-out test split
        X_test, y_test = engine.heldout_test_data
        rf_pred = engine.rf_model.predict_proba(X_test)[:, 1]
        gb_pred = engine.gb_model.predict_proba(X_test)[:, 1]
        ensemble_pred = (rf_pred * 0.55 + gb_pred * 0.45 >= 0.5).astype(int)
        independent_acc = round(float(accuracy_score(y_test, ensemble_pred)) * 100, 2)

        assert metrics["accuracy"] == independent_acc, (
            f"Reported accuracy {metrics['accuracy']} does not match independent recomputation {independent_acc}"
        )
        assert metrics["accuracy"] > 50.0

    def test_reply_engine_heldout_reproducible_evaluation(self):
        """Auto-reply classifier metrics on held-out test split match independent recomputation."""
        engine = TFIDFReplyEngine()
        metrics = engine.evaluate_on_heldout()

        # Independent recomputation on the exact held-out test split
        X_test, y_test = engine.heldout_test_data
        X_test_tfidf = engine.vectorizer.transform(X_test)
        y_pred = engine.classifier.predict(X_test_tfidf)
        independent_acc = round(float(accuracy_score(y_test, y_pred)) * 100, 2)

        assert metrics["accuracy"] == independent_acc, (
            f"Reported accuracy {metrics['accuracy']} does not match independent recomputation {independent_acc}"
        )
        assert metrics["accuracy"] > 30.0


class TestModelRegistryManager:
    """Test ModelRegistry cataloging, stage transitions, and metadata."""

    @pytest.fixture
    def registry(self):
        return ModelRegistryManager()

    def test_list_and_get_models(self, registry):
        models = registry.list_models()
        assert len(models) == 6
        names = [m.model_name for m in models]
        assert "scheduling_rf_gb_ensemble" in names
        assert "sentiment_dual_phase_vader" in names

        item = registry.get_model("sentiment_dual_phase_vader")
        assert item is not None
        assert item.stage == ModelStage.PRODUCTION
        assert item.is_production is True

    def test_promote_model_lifecycle(self, registry):
        promoted = registry.promote_model("scheduling_rf_gb_ensemble", ModelStage.STAGING)
        assert promoted.stage == ModelStage.STAGING
        assert promoted.is_production is False

        promoted_prod = registry.promote_model("scheduling_rf_gb_ensemble", ModelStage.PRODUCTION)
        assert promoted_prod.stage == ModelStage.PRODUCTION
        assert promoted_prod.is_production is True


class TestModelService:
    """Test ModelService orchestration and database interface."""

    @pytest.mark.asyncio
    async def test_get_registry_and_evaluate_single(self):
        mock_db = AsyncMock()
        service = ModelService(mock_db)

        registry_list = await service.get_model_registry()
        assert len(registry_list) >= 6

        report = await service.evaluate_single_model("sentiment")
        assert report.task == "sentiment"

        features = await service.get_feature_importance("growth")
        assert len(features) > 0

        drift = await service.check_drift("growth", current_metric=89.0)
        assert drift.drift_detected is False

        promoted = await service.promote_model(
            "scheduling_rf_gb_ensemble",
            ModelPromotionRequest(target_stage=ModelStage.PRODUCTION, reason="Verified baseline"),
        )
        assert promoted.stage == ModelStage.PRODUCTION


class TestModelAPIEndpoints:
    """Test FastAPI REST endpoints for Model Improvement & Registry."""

    def test_list_model_registry_endpoint(self):
        response = client.get("/api/v1/models/registry")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 6
        assert any(m["model_name"] == "scheduling_rf_gb_ensemble" for m in data)

    def test_evaluate_all_models_endpoint(self):
        response = client.get("/api/v1/models/evaluate-all")
        assert response.status_code == 200
        data = response.json()
        assert data["total_registered_models"] == 6
        assert len(data["models"]) == 6

    def test_evaluate_single_model_endpoint(self):
        response = client.get("/api/v1/models/scheduling/evaluation")
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "scheduling"

    def test_get_feature_importance_endpoint(self):
        response = client.get("/api/v1/models/growth/feature-importance")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["importance_score"] > 0

    def test_check_model_drift_endpoint(self):
        response = client.get("/api/v1/models/sentiment/drift?current_metric=89.2")
        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "sentiment"
        assert data["drift_detected"] is False

    def test_promote_model_endpoint(self):
        payload = {
            "target_stage": "production",
            "reason": "100% benchmark baseline achievement",
            "deployed_by": "qa_team",
        }
        response = client.post("/api/v1/models/scheduling_rf_gb_ensemble/promote", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "production"
        assert data["is_production"] is True
