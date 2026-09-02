"""Model Improvement & Registry Service - Evaluation, Drift, and Staging Management."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.app.db.models import MLModel, ModelPrediction
from backend.app.ai.evaluation.evaluator import ModelEvaluator
from backend.app.ai.registry.model_registry import ModelRegistryManager
from backend.app.core.schemas.model_eval import (
    ModelStage,
    SingleModelEvaluationReport,
    FeatureImportanceItem,
    ModelDriftReport,
    ModelMetadataItem,
    ComprehensiveModelAuditResponse,
    ModelPromotionRequest,
)


class ModelService:
    """Service handling model evaluation, feature diagnostics, drift detection, and promotion."""

    def __init__(
        self,
        db: AsyncSession,
        evaluator: Optional[ModelEvaluator] = None,
        registry: Optional[ModelRegistryManager] = None,
    ):
        self.db = db
        self.evaluator = evaluator or ModelEvaluator()
        self.registry = registry or ModelRegistryManager()

    async def get_model_registry(self) -> List[ModelMetadataItem]:
        """Fetch all models currently registered in the catalog."""
        return self.registry.list_models()

    async def get_model_by_name(self, model_name: str) -> Optional[ModelMetadataItem]:
        """Get model catalog entry by name."""
        return self.registry.get_model(model_name)

    async def evaluate_all_models(self) -> ComprehensiveModelAuditResponse:
        """Run diagnostic evaluation across all system models."""
        return self.evaluator.evaluate_all_models()

    async def evaluate_single_model(self, model_name: str) -> SingleModelEvaluationReport:
        """Evaluate a specific model by name."""
        name = model_name.lower()
        if "sched" in name:
            return self.evaluator.evaluate_scheduling_engine()
        elif "sent" in name:
            return self.evaluator.evaluate_sentiment_engine()
        elif "reply" in name:
            return self.evaluator.evaluate_auto_reply_engine()
        elif "growth" in name:
            return self.evaluator.evaluate_growth_engine()
        elif "hashtag" in name:
            return self.evaluator.evaluate_hashtag_engine()
        elif "caption" in name:
            return self.evaluator.evaluate_caption_engine()
        else:
            return self.evaluator.evaluate_scheduling_engine()

    async def get_feature_importance(self, model_name: str) -> List[FeatureImportanceItem]:
        """Get ranked feature importances for a model."""
        report = await self.evaluate_single_model(model_name)
        return report.feature_importances

    async def check_drift(self, model_name: str, current_metric: Optional[float] = None) -> ModelDriftReport:
        """Check for performance drift against baseline."""
        metric_val = current_metric or 88.0
        return self.evaluator.detect_model_drift(model_name, metric_val)

    async def promote_model(self, model_name: str, request: ModelPromotionRequest) -> ModelMetadataItem:
        """Promote model to target stage and update registry."""
        updated = self.registry.promote_model(model_name, request.target_stage)
        return updated
