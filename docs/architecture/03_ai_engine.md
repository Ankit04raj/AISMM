# AI Engine Architecture

## Overview
The AI Engine layer contains all machine learning and AI components. It is completely platform-independent — it only receives and produces **normalized** data. Each engine is swappable and versioned via the Model Registry.

---

## 1. Engine Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI ENGINE LAYER                                 │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ Scheduling   │  │  Sentiment   │  │ Engagement   │  │  Growth    │  │
│  │ Engine       │  │  Engine      │  │ Prediction   │  │ Engine     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                 │                 │                 │         │
│         └─────────────────┼─────────────────┼─────────────────┘         │
│                           ▼                 ▼                           │
│              ┌──────────────────────────────────────────────┐          │
│              │           RECOMMENDATION ENGINE              │          │
│              │  (Consumes all engine outputs, produces      │          │
│              │   prioritized recommendations with reasons)  │          │
│              └──────────────────────────────────────────────┘          │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Auto-Reply   │  │  Caption     │  │  Hashtag     │                  │
│  │ Engine       │  │  Engine      │  │  Engine      │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                          │
│  All engines implement: BaseAIEngine                                   │
│  - predict(input: NormalizedInput) -> PredictionResult                 │
│  - train(dataset: TrainingDataset) -> ModelArtifact                    │
│  - get_model_version() -> str                                          │
│  - get_model_metadata() -> ModelMetadata                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Base Engine Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class NormalizedInput:
    """Common input format for all engines."""
    user_id: str
    platform_id: Optional[str]
    account_id: Optional[str]
    features: Dict[str, Any]
    context: Dict[str, Any]

@dataclass
class PredictionResult:
    predictions: Dict[str, Any]
    confidence: float
    model_version: str
    metadata: Dict[str, Any]

@dataclass
class TrainingDataset:
    features: Any
    labels: Any
    metadata: Dict[str, Any]

@dataclass
class ModelArtifact:
    model_object: Any
    version: str
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    feature_names: List[str]
    created_at: datetime

class BaseAIEngine(ABC):
    @abstractmethod
    async def predict(self, input_data: NormalizedInput) -> PredictionResult: ...

    @abstractmethod
    async def train(self, training_data: TrainingDataset) -> ModelArtifact: ...

    @abstractmethod
    def get_model_version(self) -> str: ...

    @abstractmethod
    def get_model_metadata(self) -> ModelMetadata: ...
```

---

## 3. Engine Specifications

### 3.1 Scheduling Engine

| Aspect | Specification |
|--------|---------------|
| **Research Baseline** | Random Forest + XGBoost + Hard Voting (88.08% accuracy) |
| **Input Features** | Platform, historical posts, engagement, posting_time, day_of_week, caption_length, hashtag_count, follower_count, media_type |
| **Output** | Optimal posting time per platform (hour:minute) + confidence |
| **Platform-Aware** | Yes — learns separate patterns per platform |
| **Config** | `scheduler_config`: model_type, retrain_frequency, min_samples |

```python
class SchedulingEngine(BaseAIEngine):
    async def predict(self, input_data):
        # Features engineered from NormalizedPost history
        features = self._engineer_features(input_data)
        
        # Platform-specific model or universal with platform feature
        prediction = self._model.predict(features)
        
        return PredictionResult(
            predictions={"optimal_times": prediction.best_times},
            confidence=prediction.confidence,
            model_version=self.get_model_version(),
            metadata={"platform": input_data.platform_id}
        )
```

### 3.2 Sentiment Engine (Dual-Phase)

```python
class SentimentEngine:
    """Orchestrates PrePostAnalyzer + PostPostAnalyzer + Aggregator + TemporalAnalyzer"""
    
    async def analyze_pre_post(self, content: UniversalContent) -> SentimentResult:
        # VADER initial score
        vader_score = self._vader.polarity_scores(content.text)['compound']
        
        # k-NN refinement for ambiguous cases (-0.05 < score < 0.05)
        if -0.05 < vader_score < 0.05:
            knn_score = self._knn.predict(content.text)
            final_score = (vader_score + knn_score) / 2
        else:
            final_score = vader_score
        
        return SentimentResult(
            score=final_score,
            label=self._label_from_score(final_score),
            confidence=self._confidence_from_score(final_score),
            phase="pre_post"
        )
    
    async def analyze_post_post(self, comments: List[NormalizedComment]) -> SentimentResult:
        # Aggregate sentiment from comments over time
        scores = [c.sentiment_score for c in comments if c.sentiment_score]
        return SentimentResult(
            score=mean(scores) if scores else 0,
            label=self._label_from_score(mean(scores)),
            confidence=len(scores) / max(len(comments), 1),
            phase="post_post",
            temporal=self._temporal_analyzer.analyze(comments)
        )
```

**Thresholds (configurable):**
- `>= 0.50` → Very Positive
- `0.05 to 0.50` → Positive
- `-0.05 to 0.05` → Neutral
- `-0.50 to -0.05` → Negative
- `<= -0.50` → Very Negative

### 3.3 Auto-Reply Engine

```python
class ReplyEngine(ABC):
    @abstractmethod
    async def generate_reply(self, comment: NormalizedComment) -> ReplyResult: ...

class TFIDFReplyEngine(ReplyEngine):
    """Research baseline: TF-IDF + Multiclass Logistic Regression (88% accuracy)"""
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english', ngram_range=(1, 2), max_features=10000
        )
        self.classifier = LogisticRegression(
            multi_class='multinomial', max_iter=1000, solver='lbfgs'
        )

class LLMReplyEngine(ReplyEngine):
    """Future: LLM-based with RAG"""
    pass

class HybridReplyEngine(ReplyEngine):
    """Future: TF-IDF for speed + LLM for complex cases"""
    pass
```

**Human-in-the-Loop:**
```
Comment → ReplyEngine → Confidence
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    confidence >= 0.90      0.70-0.90            < 0.70
         │                      │                     │
         ▼                      ▼                     ▼
    AUTO REPLY           NEEDS APPROVAL        MANUAL HANDLING
```

### 3.4 Growth Engine

```python
class GrowthEngine(BaseAIEngine):
    """Platform-specific Random Forest Regressor"""
    
    async def predict(self, input_data):
        # Features: historical followers, engagement, post frequency, etc.
        # Trained per platform (IG: 89.2% R², FB: 87.5%, X: 85.8%)
        model = self._get_platform_model(input_data.platform_id)
        prediction = model.predict(input_data.features)
        
        return PredictionResult(
            predictions={
                "predicted_followers": prediction,
                "growth_rate": prediction / current_followers,
                "confidence_interval": self._get_ci(model, input_data.features)
            },
            confidence=self._model_confidence(model),
            model_version=self.get_model_version(),
            metadata={"platform": input_data.platform_id}
        )
```

### 3.5 Caption Engine

```python
class CaptionEngine(BaseAIEngine):
    """Platform-independent caption analysis & optimization"""
    
    async def analyze(self, content: UniversalContent) -> CaptionAnalysis:
        return CaptionAnalysis(
            quality_score=self._score_quality(content.caption),
            length_score=self._score_length(content.caption),
            readability=self._readability(content.caption),
            sentiment=self._sentiment_analyzer.analyze(content.caption),
            keyword_density=self._keyword_density(content.caption)
        )
    
    async def optimize(self, content: UniversalContent, 
                       platform: str) -> OptimizedCaption:
        strategy = PlatformContentStrategy.get(platform)
        return strategy.optimize(content)
```

### 3.6 Hashtag Engine

```python
class HashtagEngine(BaseAIEngine):
    """Hashtag extraction, normalization, performance analysis, Top-K recommendation"""
    
    async def extract(self, text: str) -> List[str]: ...
    async def normalize(self, tags: List[str]) -> List[str]: ...
    async def analyze_performance(self, tags: List[str], 
                                  platform: str) -> HashtagPerformance: ...
    async def recommend(self, content: UniversalContent,
                        platform: str, k: int = 5) -> List[HashtagRecommendation]: ...
```

---

## 4. Model Registry

```python
class ModelRegistry:
    """Central model management with lifecycle states."""
    
    STAGES = ["development", "staging", "production", "deprecated"]
    
    def register(self, engine_type: str, platform: Optional[str],
                 artifact: ModelArtifact, stage: str = "development") -> ModelRecord:
        """Register a new model version."""
    
    def get_production(self, engine_type: str, platform: Optional[str]) -> ModelArtifact:
        """Get current production model for engine (+ platform)."""
    
    def promote(self, model_id: str, from_stage: str, to_stage: str) -> bool:
        """Promote model between stages."""
    
    def record_performance(self, model_id: str, metrics: Dict, 
                          dataset_version: str, actual_outcomes: Dict) -> None:
        """Record post-deployment performance for drift detection."""
    
    def detect_drift(self, model_id: str, current_metrics: Dict) -> DriftReport:
        """Compare current performance to training baseline."""
    
    def recommend_retraining(self, model_id: str) -> RetrainRecommendation:
        """Based on drift, performance degradation, data staleness."""
```

**Model Record Schema:**
```python
@dataclass
class ModelRecord:
    id: str
    engine_type: str          # scheduling, sentiment, growth, etc.
    platform: Optional[str]   # None for universal models
    version: str
    stage: str                # development | staging | production | deprecated
    model_path: str           # Serialized model location
    dataset_version: str
    feature_version: str
    training_date: datetime
    metrics: Dict             # accuracy, R², RMSE, F1, etc.
    hyperparameters: Dict
    created_at: datetime
```

---

## 5. Training Pipeline

```
Raw Platform Data (from sync)
         │
         ▼
    Validation → Cleaning → Feature Engineering
         │
         ▼
   Dataset Versioning (hash of raw + feature params)
         │
         ▼
         ├─────────────────┐
         ▼                 ▼
    Train Split        Validation Split
         │                 │
         ▼                 ▼
    Model Training    →  Evaluation (metrics)
         │                 │
         ▼                 ▼
         └────────┬────────┘
                  ▼
         Model Registry (stage: development)
                  │
                  ▼
         Integration Tests → Staging → Production
                  │
                  ▼
         Performance Monitoring → Drift Detection
                  │
                  ▼
         Retraining Recommendation → New Training Cycle
```

---

## 6. Feature Engineering (Shared)

```python
class FeatureEngineer:
    """Shared feature engineering for scheduling, engagement, growth."""
    
    # Temporal features
    def hour_of_day(self, dt: datetime) -> int
    def day_of_week(self, dt: datetime) -> int
    def is_weekend(self, dt: datetime) -> bool
    def is_holiday(self, dt: datetime, country: str) -> bool
    
    # Content features
    def caption_length(self, text: str) -> int
    def hashtag_count(self, text: str) -> int
    def mention_count(self, text: str) -> int
    def media_type_encoding(self, media: List[MediaItem]) -> List[int]
    def sentiment_score(self, text: str) -> float
    
    # Account features
    def follower_count(self, account_id: str) -> int
    def following_count(self, account_id: str) -> int
    def post_frequency(self, account_id: str, window_days: int) -> float
    def avg_engagement_rate(self, account_id: str, window_days: int) -> float
    
    # Historical features
    def rolling_engagement(self, account_id: str, window_days: int) -> List[float]
    def best_historical_times(self, account_id: str) -> List[Tuple[int, float]]
```

---

## 7. Recommendation Engine

```python
class RecommendationEngine:
    """Central AI strategy — combines all engine outputs."""
    
    def __init__(self):
        self.scheduling = SchedulingEngine()
        self.sentiment = SentimentEngine()
        self.growth = GrowthEngine()
        self.engagement = EngagementPredictionEngine()
        self.caption = CaptionEngine()
        self.hashtag = HashtagEngine()
        self.auto_reply = AutoReplyEngine()
    
    async def generate_recommendation(self, context: RecommendationContext) -> List[Recommendation]:
        """Produce prioritized, explained recommendations."""
        
        # Parallel predictions
        scheduling = await self.scheduling.predict(context.scheduling_input)
        growth = await self.growth.predict(context.growth_input)
        engagement = await self.engagement.predict(context.engagement_input)
        sentiment = await self.sentiment.analyze_pre_post(context.content)
        caption = await self.caption.analyze(context.content)
        hashtags = await self.hashtag.recommend(context.content, context.platform)
        
        # Synthesis with rules + ML
        recommendations = self._synthesize(
            scheduling, growth, engagement, sentiment, caption, hashtags
        )
        
        return sorted(recommendations, key=lambda r: r.priority, reverse=True)
```

**Recommendation Output:**
```python
@dataclass
class Recommendation:
    action: str                           # "post_now", "schedule", "optimize_caption", "add_hashtags", "reply", "investigate"
    platform: str
    reason: str                           # Human-readable explanation
    confidence: float                     # 0.0 - 1.0
    priority: int                         # 1-10
    expected_impact: Dict[str, float]     # {"engagement_lift": 0.23, "growth": 0.05}
    supporting_data: Dict                 # Engine outputs that led to this
```

---

## 8. Performance Monitoring & Drift Detection

```python
class ModelMonitor:
    """Continuous monitoring of deployed models."""
    
    async def check_performance(self, model_id: str) -> PerformanceReport:
        # Compare predictions vs actual outcomes
        predictions = await self._get_predictions(model_id)
        actuals = await self._get_actuals(model_id)
        
        if len(predictions) < MIN_SAMPLES:
            return PerformanceReport(status="insufficient_data")
        
        metrics = self._compute_metrics(predictions, actuals)
        drift = self._detect_drift(metrics)
        
        return PerformanceReport(
            metrics=metrics,
            drift=drift,
            recommendation=self._recommend_action(drift, metrics)
        )
```

---

## 9. Configuration

```yaml
# config/ai_models.yaml
models:
  scheduling:
    type: "random_forest_xgboost_voting"
    platform_specific: true
    retrain_frequency_days: 7
    min_training_samples: 100
    features:
      - temporal: [hour, day_of_week, is_weekend]
      - content: [caption_length, hashtag_count, media_type]
      - account: [follower_count, avg_engagement_rate]
  
  sentiment:
    type: "vader_knn"
    knn_k: 5
    thresholds:
      very_positive: 0.50
      positive: 0.05
      neutral: 0.0
      negative: -0.05
      very_negative: -0.50
  
  auto_reply:
    type: "tfidf_logistic"
    tfidf:
      ngram_range: [1, 2]
      max_features: 10000
    logistic:
      max_iter: 1000
      solver: "lbfgs"
    confidence_thresholds:
      auto: 0.90
      approval: 0.70
      manual: 0.0
  
  growth:
    type: "random_forest_regressor"
    platform_specific: true
    target: "follower_count"
    features:
      - historical_followers
      - engagement_metrics
      - post_frequency
      - content_types
  
  caption:
    type: "statistical_template"
    platforms: ["instagram", "facebook", "x", "linkedin", "youtube"]
  
  hashtag:
    type: "frequency_topk"
    top_k: 5
    min_frequency: 3
```

---

*Document Version: 1.0 — Phase 2 Architecture Design*
