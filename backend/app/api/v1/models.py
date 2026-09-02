"""Model Evaluation, Registry, and Improvement API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.model_service import ModelService
from backend.app.core.schemas.model_eval import (
    ModelMetadataItem,
    SingleModelEvaluationReport,
    FeatureImportanceItem,
    ModelDriftReport,
    ComprehensiveModelAuditResponse,
    ModelPromotionRequest,
)

router = APIRouter(prefix="/models", tags=["Model Improvement & Registry"])


@router.get("/registry", response_model=List[ModelMetadataItem])
async def list_model_registry(
    db: AsyncSession = Depends(get_db),
):
    """List all registered ML models, versions, stages, and hyperparameters."""
    service = ModelService(db)
    return await service.get_model_registry()


@router.get("/evaluate-all", response_model=ComprehensiveModelAuditResponse)
async def evaluate_all_models(
    db: AsyncSession = Depends(get_db),
):
    """Run full diagnostic benchmark comparing current performance with research baselines."""
    service = ModelService(db)
    return await service.evaluate_all_models()


@router.get("/{model_name}/evaluation", response_model=SingleModelEvaluationReport)
async def evaluate_single_model(
    model_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed accuracy, latency, and diagnostic metrics for a specific model."""
    service = ModelService(db)
    return await service.evaluate_single_model(model_name)


@router.get("/{model_name}/feature-importance", response_model=List[FeatureImportanceItem])
async def get_feature_importance(
    model_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get ranked feature importances for tree-based and heuristic models."""
    service = ModelService(db)
    return await service.get_feature_importance(model_name)


@router.get("/{model_name}/drift", response_model=ModelDriftReport)
async def check_model_drift(
    model_name: str,
    current_metric: Optional[float] = Query(None, description="Latest evaluated metric to test against baseline"),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate metric drift and determine if model retraining is recommended."""
    service = ModelService(db)
    return await service.check_drift(model_name, current_metric=current_metric)


@router.post("/{model_name}/promote", response_model=ModelMetadataItem)
async def promote_model(
    model_name: str,
    request: ModelPromotionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Transition a model's deployment stage (development -> staging -> production)."""
    service = ModelService(db)
    return await service.promote_model(model_name, request)
