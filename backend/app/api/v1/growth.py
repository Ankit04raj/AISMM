"""Predictive Growth Engine API router."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.growth_service import GrowthService
from backend.app.core.schemas.growth import (
    GrowthPredictRequest,
    GrowthPredictResponse,
    AccountGrowthProjectionResponse,
    GrowthModelStatusItem,
)

router = APIRouter(prefix="/growth", tags=["Predictive Growth Engine"])


@router.post("/predict", response_model=GrowthPredictResponse)
async def predict_growth(
    request: GrowthPredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict follower trajectory and reach across 7, 30, and 90 day horizons using Random Forest."""
    service = GrowthService(db)
    return await service.predict_growth(request)


@router.get("/accounts/{account_id}/projections", response_model=AccountGrowthProjectionResponse)
async def get_account_growth_projections(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and store predictive growth projections for a connected social account owned by user."""
    service = GrowthService(db)
    return await service.get_account_projections(UUID(account_id), current_user.id)


@router.get("/models/status", response_model=List[GrowthModelStatusItem])
async def get_growth_models_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active platform growth regression models and accuracy metrics (R2 and RMSE)."""
    service = GrowthService(db)
    return service.get_models_status()
