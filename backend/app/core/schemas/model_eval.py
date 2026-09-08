"""Pydantic schemas for Phase 15 Model Improvement, Evaluation, and Registry."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ModelStage(str, Enum):
    """Lifecycle stage for machine learning models."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class FeatureImportanceItem(BaseModel):
    """Ranked feature importance score from tree-based or regression models."""
    feature_name: str
    importance_score: float
    relative_percentage: float
    description: Optional[str] = None


class ClassImbalanceItem(BaseModel):
    """Class frequency and balance analysis."""
    class_name: str
    sample_count: int
    proportion_percent: float
    assigned_class_weight: float
    status: str  # "balanced", "moderate_imbalance", "severe_imbalance"


class ConfusionMatrixData(BaseModel):
    """Confusion matrix metrics representation."""
    labels: List[str]
    matrix: List[List[int]]
    precision_per_class: Dict[str, float]
    recall_per_class: Dict[str, float]
    f1_per_class: Dict[str, float]


class SingleModelEvaluationReport(BaseModel):
    """Detailed evaluation report for a specific ML model."""
    model_name: str
    model_version: str
    model_type: str  # "classification", "regression", "ranking", "ensemble"
    framework: str
    task: str  # "scheduling", "sentiment", "auto_reply", "growth", "caption", "hashtag"
    stage: ModelStage
    evaluation_dataset_size: int
    latency_ms: float

    # Core performance metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    r2_score: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    top_k_accuracy: Optional[float] = None

    # Research baseline comparison
    research_baseline_metric: float
    current_vs_baseline_delta: float
    meets_research_baseline: bool

    # Advanced diagnostics
    feature_importances: List[FeatureImportanceItem] = Field(default_factory=list)
    class_balance: List[ClassImbalanceItem] = Field(default_factory=list)
    confusion_matrix: Optional[ConfusionMatrixData] = None
    drift_status: str  # "calibrated", "mild_drift", "retraining_recommended"
    evaluated_at: datetime


class ModelDriftReport(BaseModel):
    """Model performance drift and decay tracking."""
    model_name: str
    model_version: str
    baseline_metric_value: float
    current_metric_value: float
    metric_name: str
    drift_percentage: float
    drift_detected: bool
    retraining_recommended: bool
    diagnostics: List[str] = Field(default_factory=list)
    checked_at: datetime


class ModelMetadataItem(BaseModel):
    """Model catalog entry in the ModelRegistry."""
    model_id: str
    model_name: str
    version: str
    stage: ModelStage
    model_type: str
    framework: str
    description: str
    is_production: bool
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    average_latency_ms: float
    created_at: datetime
    deployed_at: Optional[datetime] = None


class ComprehensiveModelAuditResponse(BaseModel):
    """Master AI model audit aggregating evaluation across all active system models."""
    models: List[SingleModelEvaluationReport]
    total_registered_models: int
    production_models_count: int
    system_average_latency_ms: float
    all_models_meeting_baselines: bool
    generated_at: datetime


class ModelPromotionRequest(BaseModel):
    """Request payload to promote or change the deployment stage of a model."""
    target_stage: ModelStage
    reason: Optional[str] = "Performance verified against research baseline"
    deployed_by: Optional[str] = "system_admin"
