"""ML Model and Prediction models."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, Text, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class ModelStatus(str, enum.Enum):
    """Model deployment status."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class ModelType(str, enum.Enum):
    """Model type."""
    SCHEDULING = "scheduling"
    SENTIMENT = "sentiment"
    GROWTH = "growth"
    REPLY = "reply"
    CAPTION = "caption"
    HASHTAG = "hashtag"
    RECOMMENDATION = "recommendation"


class MLModel(Base):
    """ML Model registry entry."""

    __tablename__ = "ml_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[ModelType] = mapped_column(SQLEnum(ModelType), nullable=False, index=True)
    status: Mapped[ModelStatus] = mapped_column(
        SQLEnum(ModelStatus), default=ModelStatus.DEVELOPMENT, nullable=False, index=True
    )
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(50), nullable=False)
    hyperparameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    trained_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    predictions: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction", back_populates="model", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_ml_models_name_version", "name", "version", unique=True),
        Index("ix_ml_models_type_status", "type", "status"),
    )

    def __repr__(self) -> str:
        return f"<MLModel(name={self.name}, version={self.version}, type={self.type}, status={self.status})>"


class ModelPrediction(Base):
    """Logged model prediction for monitoring."""

    __tablename__ = "model_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    input_features: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    predicted_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prediction_probabilities: Mapped[Dict[str, float]] = mapped_column(JSON, default=dict)
    actual_outcome: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    model: Mapped["MLModel"] = relationship("MLModel", back_populates="predictions")

    __table_args__ = (
        Index("ix_model_predictions_model_time", "model_name", "predicted_at"),
        Index("ix_model_predictions_resolved", "resolved_at"),
    )

    def __repr__(self) -> str:
        return f"<ModelPrediction(model={self.model_name}, task={self.task_type}, predicted_at={self.predicted_at})>"
