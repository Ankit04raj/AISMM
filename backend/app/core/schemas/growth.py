"""Pydantic schemas for Phase 11 Predictive Growth Engine."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class HorizonPredictionItem(BaseModel):
    """Prediction for a single time horizon."""
    horizon_days: int
    predicted_followers: int
    net_growth_followers: int
    growth_rate_percent: float
    predicted_reach: int
    confidence_r2: float
    rmse: float


class GrowthPredictRequest(BaseModel):
    """Request for growth prediction."""
    platform: str = Field(default="instagram")
    current_followers: int = Field(..., ge=0)
    posting_frequency_weekly: float = Field(default=3.0, ge=0.1, le=50.0)
    avg_engagement_rate: float = Field(default=4.0, ge=0.0, le=100.0)
    followers_gained_7d: Optional[int] = None
    followers_gained_30d: Optional[int] = None
    video_ratio: float = Field(default=0.3, ge=0.0, le=1.0)
    carousel_ratio: float = Field(default=0.2, ge=0.0, le=1.0)
    avg_sentiment_score: float = Field(default=0.4, ge=-1.0, le=1.0)


class GrowthPredictResponse(BaseModel):
    """Response containing multi-horizon growth projections."""
    platform: str
    current_followers: int
    current_engagement_rate: float
    projections: Dict[str, HorizonPredictionItem]  # "7d", "30d", "90d"
    feature_importances: Dict[str, float]
    model_version: str
    baseline_r2: float
    generated_at: datetime


class AccountGrowthProjectionResponse(BaseModel):
    """Projections linked directly to a registered social account."""
    account_id: str
    platform: str
    username: str
    current_followers: int
    projections: Dict[str, HorizonPredictionItem]
    model_version: str
    confidence_r2: float
    generated_at: datetime


class GrowthModelStatusItem(BaseModel):
    """Status and accuracy metrics of a platform growth regression model."""
    platform: str
    model_type: str = "RandomForestRegressor"
    r2_score: float
    target_baseline_r2: float
    rmse: float
    is_production: bool = True
