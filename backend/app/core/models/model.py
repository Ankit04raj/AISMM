"""ML Model registry models."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Index, JSON, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.models.base import Base, TimestampMixin


class ModelType(PyEnum):
    """ML model types."""
    SCHEDULING = "scheduling"
    SENTIMENT = "sentiment"
    GROWTH = "growth"
    REPLY = "reply"
    CAPTION = "caption"
    HASHTAG = "hashtag"
    RECOMMENDATION = "recommendation"
    ENSEMBLE = "ensemble"


class ModelStatus(PyEnum):
    """Model deployment status."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class MLModel(Base, TimestampMixin):
    """ML Model registry entry."""

    __tablename__ = "ml_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Model identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[ModelType] = mapped_column(Enum(ModelType), nullable=False, index=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    # Status
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus), default=ModelStatus.DEVELOPMENT, nullable=False, index=True
    )

    # Training metadata
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(50), nullable=False)
    hyperparameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Training info
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    training_duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    training_samples: Mapped[Optional[int]] = mapped_column(nullable=True)
    validation_samples: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Model artifact
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    model_format: Mapped[str] = mapped_column(String(20), default="joblib", nullable=False)
    model_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Feature schema (for validation)
    feature_schema: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    predictions: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction", back_populates="model", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_ml_models_name_version", "name", "version", unique=True),
        Index("ix_ml_models_type_platform_status", "type", "platform", "status"),
        Index("ix_ml_models_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<MLModel(name={self.name}, version={self.version}, type={self.type.value}, status={self.status.value})>"


class ModelPrediction(Base, TimestampMixin):
    """Model prediction log for performance monitoring."""

    __tablename__ = "model_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Input features
    input_features: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    feature_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Prediction
    predicted_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    predicted_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prediction_probabilities: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Task context
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # regression, classification
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # post, account, comment
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Actual outcome (filled later for monitoring)
    actual_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    actual_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timing
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Metadata
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    model: Mapped["MLModel"] = relationship("MLModel", back_populates="predictions")

    # Indexes
    __table_args__ = (
        Index("ix_model_predictions_model_predicted", "model_id", "predicted_at"),
        Index("ix_model_predictions_entity", "entity_type", "entity_id"),
        Index("ix_model_predictions_resolved", "resolved_at"),
    )

    def __repr__(self) -> str:
        return f"<ModelPrediction(id={self.id}, model_id={self.model_id}, entity={self.entity_type}:{self.entity_id})>"