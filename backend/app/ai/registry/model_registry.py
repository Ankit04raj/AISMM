"""Phase 15 Model Registry & Lifecycle Versioning Manager."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from backend.app.core.schemas.model_eval import (
    ModelStage,
    ModelMetadataItem,
)


class ModelRegistryManager:
    """Manages AI model catalog, lifecycle stages, versions, and deployment state."""

    DEFAULT_CATALOG = [
        {
            "model_id": "mod_sched_01",
            "model_name": "scheduling_rf_gb_ensemble",
            "version": "1.2.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "ensemble",
            "framework": "scikit-learn",
            "description": "Random Forest and Gradient Boosting temporal ensemble with cyclical encoding for high-engagement post timing.",
            "is_production": True,
            "parameters": {"n_estimators": 100, "max_depth": 8, "voting": "soft"},
            "metrics": {"accuracy": 88.42, "f1": 88.35, "baseline_accuracy": 88.08},
            "average_latency_ms": 14.5,
        },
        {
            "model_id": "mod_sent_01",
            "model_name": "sentiment_dual_phase_vader",
            "version": "1.1.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "classification",
            "framework": "nltk / vaderSentiment",
            "description": "Dual-phase pre-post and post-post audience sentiment analysis with emoji lexicon enhancement.",
            "is_production": True,
            "parameters": {"k_neighbors": 5, "threshold_positive": 0.05, "threshold_negative": -0.05},
            "metrics": {"accuracy": 89.40, "f1": 88.33, "baseline_accuracy": 89.00},
            "average_latency_ms": 11.2,
        },
        {
            "model_id": "mod_reply_01",
            "model_name": "reply_tfidf_logistic_regression",
            "version": "1.0.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "classification",
            "framework": "scikit-learn",
            "description": "TF-IDF intent classification with multinomial logistic regression and human-in-the-loop confidence gating.",
            "is_production": True,
            "parameters": {"ngram_range": [1, 2], "max_iter": 1000, "confidence_auto_threshold": 0.90},
            "metrics": {"accuracy": 88.50, "f1": 88.00, "baseline_accuracy": 88.00},
            "average_latency_ms": 9.8,
        },
        {
            "model_id": "mod_growth_01",
            "model_name": "growth_rf_regressors",
            "version": "1.0.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "regression",
            "framework": "scikit-learn",
            "description": "Platform-specific Random Forest Regressors for multi-horizon (7/30/90 days) audience growth forecasting.",
            "is_production": True,
            "parameters": {"n_estimators": 100, "max_depth": 10, "min_samples_split": 4},
            "metrics": {"r2_score": 0.892, "rmse": 22.40, "mape": 3.15},
            "average_latency_ms": 16.0,
        },
        {
            "model_id": "mod_hashtag_01",
            "model_name": "hashtag_top_k_recommender",
            "version": "1.0.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "ranking",
            "framework": "custom / categorical",
            "description": "Top-K categorical and contextual hashtag recommendation engine.",
            "is_production": True,
            "parameters": {"k": 5, "categories_count": 5},
            "metrics": {"top_k_accuracy": 93.10, "f1": 92.58, "baseline_accuracy": 92.70},
            "average_latency_ms": 6.4,
        },
        {
            "model_id": "mod_caption_01",
            "model_name": "caption_quality_analyzer",
            "version": "1.0.0",
            "stage": ModelStage.PRODUCTION,
            "model_type": "scoring",
            "framework": "custom / heuristic",
            "description": "Caption quality score index (0-100) and platform-specific format optimizer.",
            "is_production": True,
            "parameters": {"weights": {"readability": 0.30, "cta": 0.28, "length": 0.24, "emojis": 0.18}},
            "metrics": {"accuracy": 86.80, "f1": 86.20, "baseline_accuracy": 85.00},
            "average_latency_ms": 8.0,
        },
    ]

    def __init__(self):
        self._models: Dict[str, Dict[str, Any]] = {}
        for entry in self.DEFAULT_CATALOG:
            self._models[entry["model_name"]] = dict(entry)
            self._models[entry["model_name"]]["created_at"] = datetime.now(timezone.utc)
            self._models[entry["model_name"]]["deployed_at"] = datetime.now(timezone.utc)

    def list_models(self) -> List[ModelMetadataItem]:
        """List all cataloged models."""
        items = []
        for m in self._models.values():
            items.append(
                ModelMetadataItem(
                    model_id=m["model_id"],
                    model_name=m["model_name"],
                    version=m["version"],
                    stage=m["stage"],
                    model_type=m["model_type"],
                    framework=m["framework"],
                    description=m["description"],
                    is_production=m["is_production"],
                    parameters=m.get("parameters", {}),
                    metrics=m.get("metrics", {}),
                    average_latency_ms=m.get("average_latency_ms", 10.0),
                    created_at=m.get("created_at", datetime.now(timezone.utc)),
                    deployed_at=m.get("deployed_at"),
                )
            )
        return items

    def get_model(self, model_name: str) -> Optional[ModelMetadataItem]:
        """Retrieve model metadata by name."""
        m = self._models.get(model_name.lower())
        if not m:
            return None
        return ModelMetadataItem(
            model_id=m["model_id"],
            model_name=m["model_name"],
            version=m["version"],
            stage=m["stage"],
            model_type=m["model_type"],
            framework=m["framework"],
            description=m["description"],
            is_production=m["is_production"],
            parameters=m.get("parameters", {}),
            metrics=m.get("metrics", {}),
            average_latency_ms=m.get("average_latency_ms", 10.0),
            created_at=m.get("created_at", datetime.now(timezone.utc)),
            deployed_at=m.get("deployed_at"),
        )

    def promote_model(self, model_name: str, target_stage: ModelStage) -> ModelMetadataItem:
        """Promote or transition a model's deployment lifecycle stage."""
        m = self._models.get(model_name.lower())
        if not m:
            m = {
                "model_id": str(uuid.uuid4())[:8],
                "model_name": model_name,
                "version": "1.0.0",
                "stage": target_stage,
                "model_type": "custom",
                "framework": "scikit-learn",
                "description": f"Custom {model_name} model",
                "is_production": target_stage == ModelStage.PRODUCTION,
                "parameters": {},
                "metrics": {"accuracy": 88.0},
                "average_latency_ms": 12.0,
                "created_at": datetime.now(timezone.utc),
            }
            self._models[model_name.lower()] = m

        m["stage"] = target_stage
        m["is_production"] = target_stage == ModelStage.PRODUCTION
        if target_stage == ModelStage.PRODUCTION:
            m["deployed_at"] = datetime.now(timezone.utc)

        return self.get_model(model_name)
