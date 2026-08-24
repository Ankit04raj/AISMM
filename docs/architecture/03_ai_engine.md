# AISMM AI Engine Architecture
**Phase 2 — Architecture Design**  
**Version:** 1.0  
**Date:** 2026-08-25  
**Status:** DESIGN — AWAITING APPROVAL

---

## 1. AI Engine Overview

The AI Engine is the intelligence layer of AISMM. It receives **normalized data** from platform adapters and produces **platform-independent insights, predictions, and recommendations**.

### Core Principle
> **AI Core is platform-independent. It receives normalized data, not raw platform API objects.**

### Engine Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI ENGINE LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Sentiment   │  │  Scheduling  │  │   Growth     │              │
│  │   Engine     │  │   Engine     │  │   Engine     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                      │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐              │
│  │   Caption    │  │   Hashtag    │  │   Auto-Reply │              │
│  │   Engine     │  │   Engine     │  │   Engine     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                        │
│                  ┌────────┴────────┐                               │
│                  │ Recommendation  │                               │
│                  │    Engine       │                               │
│                  └────────┬────────┘                               │
│                           │                                        │
│                    ┌──────┴──────┐                                 │
│                    │   Model     │                                 │
│                    │  Registry   │                                 │
│                    └─────────────┘                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Normalized Input Data Models

All AI engines receive standardized input:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

@dataclass
class NormalizedPost:
    id: str
    user_id: str
    platform: str
    platform_post_id: Optional[str]
    content: str
    caption: Optional[str]
    hashtags: List[str]
    mentions: List[str]
    media: List[Dict]
    status: PostStatus
    created_at: datetime
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    engagement: Dict[str, int]  # normalized metric types
    metadata: Dict

@dataclass
class NormalizedEngagement:
    post_id: str
    platform: str
    metrics: Dict[str, int]  # LIKE, COMMENT, SHARE, REACTION, VIEW, etc.
    original_metrics: Dict[str, int]
    timestamp: datetime

@dataclass
class NormalizedComment:
    id: str
    post_id: str
    platform: str
    platform_comment_id: str
    author: Dict
    content: str
    created_at: datetime
    sentiment: Optional[Dict] = None
    replies: List["NormalizedComment"] = field(default_factory=list)

@dataclass
class NormalizedAudience:
    platform: str
    account_id: str
    follower_count: int
    demographics: Dict  # age, gender, location, interests
    engagement_rate: float
    active_hours: List[int]  # 0-23
    timestamp: datetime

@dataclass
class NormalizedTimestamp:
    platform: str
    hour: int          # 0-23
    day_of_week: int   # 0-6 (Monday=0)
    is_weekend: bool
    month: int
    timezone: str
```

---

## 3. Feature Engineering Pipeline

### Shared Feature Store

```python
# backend/app/ai/feature_store.py

class FeatureStore:
    """Centralized feature engineering for all AI engines."""
    
    def __init__(self):
        self._extractors = {}
    
    def register_extractor(self, name: str, extractor: "FeatureExtractor"):
        self._extractors[name] = extractor
    
    def extract_all(self, entity_type: str, data: Dict) -> Dict:
        """Extract all registered features for entity type."""
        features = {}
        for name, extractor in self._extractors.items():
            if extractor.applies_to(entity_type):
                features[name] = extractor.extract(data)
        return features

class FeatureExtractor(ABC):
    @abstractmethod
    def applies_to(self, entity_type: str) -> bool:
        pass
    
    @abstractmethod
    def extract(self, data: Dict) -> Dict:
        pass

# Scheduling features
class SchedulingFeatureExtractor(FeatureExtractor):
    def applies_to(self, entity_type: str) -> bool:
        return entity_type == "post"
    
    def extract(self, post: NormalizedPost) -> Dict:
        ts = post.published_at or post.scheduled_at or post.created_at
        return {
            "hour": ts.hour,
            "day_of_week": ts.weekday(),
            "is_weekend": ts.weekday() >= 5,
            "caption_length": len(post.caption or post.content),
            "hashtag_count": len(post.hashtags),
            "mention_count": len(post.mentions),
            "media_count": len(post.media),
            "media_type": self._primary_media_type(post.media),
            "has_location": bool(post.metadata.get("location")),
        }
    
    def _primary_media_type(self, media: List[Dict]) -> str:
        if not media:
            return "none"
        return media[0].get("type", "image")

# Engagement features
class EngagementFeatureExtractor(FeatureExtractor):
    def applies_to(self, entity_type: str) -> bool:
        return entity_type == "post"
    
    def extract(self, post: NormalizedPost) -> Dict:
        total = sum(post.engagement.values())
        return {
            "total_engagement": total,
            "engagement_rate": total / max(1, post.metadata.get("followers", 1)),
            "like_ratio": post.engagement.get("LIKE", 0) / max(1, total),
            "comment_ratio": post.engagement.get("COMMENT", 0) / max(1, total),
            "share_ratio": post.engagement.get("SHARE", 0) / max(1, total),
        }

# Sentiment features
class SentimentFeatureExtractor(FeatureExtractor):
    def applies_to(self, entity_type: str) -> bool:
        return entity_type in ("post", "comment")
    
    def extract(self, data: NormalizedPost | NormalizedComment) -> Dict:
        # VADER + k-NN features
        vader_scores = self._vader_scores(data.content)
        return {
            "vader_compound": vader_scores["compound"],
            "vader_positive": vader_scores["pos"],
            "vader_negative": vader_scores["neg"],
            "vader_neutral": vader_scores["neu"],
            "exclamation_count": data.content.count("!"),
            "question_count": data.content.count("?"),
            "uppercase_ratio": sum(1 for c in data.content if c.isupper()) / max(1, len(data.content)),
        }
```

---

## 4. Individual Engine Specifications

### 4.1 Sentiment Engine (Dual-Phase)

```python
# backend/app/ai/sentiment/engine.py

class SentimentEngine:
    """Dual-phase sentiment analysis: Pre-Post + Post-Post."""
    
    def __init__(self, config: SentimentConfig, model_registry: ModelRegistry):
        self.config = config
        self.model_registry = model_registry
        self.pre_analyzer = PrePostAnalyzer(config, model_registry)
        self.post_analyzer = PostPostAnalyzer(config, model_registry)
        self.aggregator = SentimentAggregator(config)
        self.temporal_analyzer = TemporalAnalyzer(config)
    
    async def analyze_pre_post(self, content: UniversalContent) -> SentimentResult:
        """Analyze sentiment before publishing."""
        return await self.pre_analyzer.analyze(content)
    
    async def analyze_post_post(self, comments: List[NormalizedComment]) -> SentimentResult:
        """Analyze audience sentiment after publishing."""
        return await self.post_analyzer.analyze(comments)
    
    async def get_aggregated_sentiment(self, post_id: str) -> AggregatedSentiment:
        """Get combined pre/post sentiment with temporal analysis."""
        pre = await self.pre_analyzer.get_latest(post_id)
        post = await self.post_analyzer.get_latest(post_id)
        temporal = await self.temporal_analyzer.analyze(post_id)
        return self.aggregator.aggregate(pre, post, temporal)

class PrePostAnalyzer:
    """VADER + k-NN refinement for pre-post analysis."""
    
    def __init__(self, config: SentimentConfig, model_registry: ModelRegistry):
        self.vader = SentimentIntensityAnalyzer()
        self.knn_model = model_registry.get_model("sentiment_knn")
        self.config = config
    
    async def analyze(self, content: UniversalContent) -> SentimentResult:
        # VADER initial score
        vader_score = self.vader.polarity_scores(content.caption or content.text)
        
        # k-NN refinement for ambiguous cases (-0.05 to 0.05)
        if -0.05 < vader_score["compound"] < 0.05 and self.knn_model:
            knn_score = await self.knn_model.predict(content)
            final_score = (vader_score["compound"] + knn_score) / 2
        else:
            final_score = vader_score["compound"]
        
        return SentimentResult(
            score=final_score,
            label=self._label_from_score(final_score),
            confidence=self._confidence(final_score),
            method="vader_knn" if -0.05 < vader_score["compound"] < 0.05 else "vader",
            details=vader_score
        )
    
    def _label_from_score(self, score: float) -> str:
        thresholds = self.config.thresholds
        if score >= thresholds.very_positive: return "very_positive"
        if score >= thresholds.positive: return "positive"
        if score > thresholds.neutral: return "neutral"
        if score >= thresholds.negative: return "negative"
        return "very_negative"

class PostPostAnalyzer:
    """Analyze sentiment from comments/replies."""
    
    async def analyze(self, comments: List[NormalizedComment]) -> SentimentResult:
        if not comments:
            return SentimentResult(score=0, label="neutral", confidence=0)
        
        scores = [c.sentiment["score"] for c in comments if c.sentiment]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return SentimentResult(
            score=avg_score,
            label=self._label_from_score(avg_score),
            confidence=min(1.0, len(scores) / 10),  # More comments = higher confidence
            method="comment_aggregation",
            sample_size=len(scores)
        )
```

### 4.2 Scheduling Engine (Research Baseline: RF + XGBoost + Hard Voting)

```python
# backend/app/ai/scheduling/engine.py

class SchedulingEngine:
    """Platform-aware optimal posting time prediction."""
    
    def __init__(self, config: SchedulerConfig, model_registry: ModelRegistry,
                 feature_store: FeatureStore):
        self.config = config
        self.model_registry = model_registry
        self.feature_store = feature_store
        self.model = model_registry.get_model(config.active_model)
    
    async def predict_optimal_time(self, 
                                   platform: str,
                                   account_id: str,
                                   content: UniversalContent,
                                   constraints: TimeConstraints = None) -> TimeRecommendation:
        """Predict best posting time for platform + content."""
        
        # 1. Get platform-specific model
        model = self.model_registry.get_model(f"scheduling_{platform}")
        
        # 2. Get historical data for feature engineering
        historical = await self._get_historical_data(account_id, platform)
        
        # 3. Extract features
        features = self.feature_store.extract_all("post", {
            **content.__dict__,
            "platform": platform,
            "account": account_id,
            "historical": historical
        })
        
        # 4. Generate candidate times (next 7 days, 30-min intervals)
        candidates = self._generate_candidates(constraints)
        
        # 5. Score each candidate
        predictions = []
        for candidate in candidates:
            candidate_features = {**features, "candidate_hour": candidate.hour, 
                                 "candidate_dow": candidate.weekday()}
            score = await self._predict_engagement(model, candidate_features)
            predictions.append((candidate, score))
        
        # 6. Sort and return top recommendations
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return TimeRecommendation(
            platform=platform,
            recommendations=predictions[:5],
            constraints=constraints,
            model_version=model.version
        )
    
    async def _predict_engagement(self, model, features: Dict) -> float:
        """Use ensemble: RF + XGBoost + Hard Voting."""
        rf_score = model.rf_model.predict_proba([features])[0][1]
        xgb_score = model.xgb_model.predict_proba([features])[0][1]
        
        # Hard voting (research baseline)
        return (rf_score + xgb_score) / 2

class SchedulingModel:
    """Platform-specific scheduling model."""
    
    def __init__(self, platform: str, version: str):
        self.platform = platform
        self.version = version
        self.rf_model = None  # RandomForestClassifier
        self.xgb_model = None  # XGBClassifier
        self.feature_names = []
        self.trained_at = None
        self.metrics = {}  # accuracy, precision, recall
```

### 4.3 Growth Engine (Platform-Specific Random Forest Regressor)

```python
# backend/app/ai/growth/engine.py

class GrowthEngine:
    """Platform-specific growth prediction using Random Forest Regressor."""
    
    def __init__(self, config: GrowthConfig, model_registry: ModelRegistry):
        self.config = config
        self.model_registry = model_registry
    
    async def train_platform_model(self, platform: str, 
                                   training_data: List[GrowthTrainingSample]) -> GrowthModel:
        """Train platform-specific growth model."""
        
        model = GrowthModel(
            platform=platform,
            model_type="random_forest",
            version=f"v{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
        )
        
        # Features: historical followers, engagement, post frequency, etc.
        X, y = self._prepare_features(training_data)
        
        # Train Random Forest Regressor
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        rf.fit(X, y)
        
        # Evaluate
        y_pred = rf.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        model.rf_model = rf
        model.r2 = r2
        model.rmse = rmse
        model.feature_importance = dict(zip(X.columns, rf.feature_importances_))
        
        # Save to registry
        await self.model_registry.register(model)
        
        return model
    
    async def predict_growth(self, platform: str, 
                            account_id: str,
                            horizon_days: int = 30) -> GrowthPrediction:
        """Predict future growth."""
        
        model = self.model_registry.get_model(f"growth_{platform}")
        if not model:
            raise ModelNotFoundError(f"No growth model for {platform}")
        
        current_metrics = await self._get_current_metrics(account_id)
        future_features = self._project_features(current_metrics, horizon_days)
        
        predicted_followers = model.rf_model.predict([future_features])[0]
        
        return GrowthPrediction(
            platform=platform,
            account_id=account_id,
            current_followers=current_metrics.followers,
            predicted_followers=int(predicted_followers),
            horizon_days=horizon_days,
            confidence=model.r2,
            model_version=model.version
        )
```

### 4.4 Auto-Reply Engine (TF-IDF + Logistic Regression)

```python
# backend/app/ai/reply/engine.py

class ReplyEngine(ABC):
    """Abstract base for reply engines."""
    
    @abstractmethod
    async def classify_comment(self, comment: NormalizedComment) -> ReplyClassification:
        pass
    
    @abstractmethod
    async def generate_reply(self, comment: NormalizedComment, 
                            classification: ReplyClassification) -> ReplySuggestion:
        pass

class TFIDFReplyEngine(ReplyEngine):
    """Research baseline: TF-IDF + Multiclass Logistic Regression."""
    
    def __init__(self, config: ReplyConfig, model_registry: ModelRegistry):
        self.config = config
        self.tfidf = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=10000
        )
        self.classifier = LogisticRegression(
            multi_class="multinomial",
            max_iter=1000,
            random_state=42
        )
        self.model_registry = model_registry
        self.reply_templates = self._load_templates()
    
    async def classify_comment(self, comment: NormalizedComment) -> ReplyClassification:
        """Classify comment into category for reply selection."""
        
        # Vectorize comment
        vector = self.tfidf.transform([comment.content])
        
        # Predict category
        category = self.classifier.predict(vector)[0]
        probabilities = self.classifier.predict_proba(vector)[0]
        confidence = max(probabilities)
        
        return ReplyClassification(
            category=category,
            confidence=confidence,
            all_probabilities=dict(zip(self.classifier.classes_, probabilities))
        )
    
    async def generate_reply(self, comment: NormalizedComment,
                            classification: ReplyClassification) -> ReplySuggestion:
        """Generate reply based on category."""
        
        templates = self.reply_templates.get(classification.category, [])
        if not templates:
            return ReplySuggestion(
                text="Thank you for your comment!",
                confidence=0.3,
                requires_approval=True
            )
        
        # Select best template (could be enhanced with LLM later)
        reply_text = self._select_template(comment, templates)
        
        return ReplySuggestion(
            text=reply_text,
            confidence=classification.confidence,
            requires_approval=classification.confidence < self.config.auto_threshold
        )

class ReplyClassification:
    category: str
    confidence: float
    all_probabilities: Dict[str, float]

class ReplySuggestion:
    text: str
    confidence: float
    requires_approval: bool
    alternative_suggestions: List[str] = []
```

### 4.5 Caption Engine

```python
# backend/app/ai/caption/engine.py

class CaptionEngine:
    """Platform-independent caption analysis and optimization."""
    
    def __init__(self, config: CaptionConfig, model_registry: ModelRegistry):
        self.config = config
        self.model_registry = model_registry
    
    async def analyze_caption(self, caption: str, platform: str) -> CaptionAnalysis:
        """Analyze caption quality and predict performance."""
        
        features = {
            "length": len(caption),
            "hashtag_count": len(re.findall(r'#\w+', caption)),
            "mention_count": len(re.findall(r'@\w+', caption)),
            "emoji_count": len(re.findall(r'[\U0001F600-\U0001F64F]', caption)),
            "question_count": caption.count("?"),
            "exclamation_count": caption.count("!"),
            "cta_present": bool(re.search(r'\b(link in bio|click|check out|learn more)\b', caption, re.I)),
        }
        
        # Platform-specific scoring
        platform_limits = self.config.platform_limits.get(platform, {})
        
        score = self._calculate_quality_score(features, platform_limits)
        
        return CaptionAnalysis(
            score=score,
            features=features,
            suggestions=self._generate_suggestions(features, platform_limits),
            platform_optimized=self._optimize_for_platform(caption, platform)
        )
    
    def _optimize_for_platform(self, caption: str, platform: str) -> str:
        """Generate platform-optimized variant."""
        
        limits = self.config.platform_limits.get(platform, {})
        max_length = limits.get("caption_max_length", 2200)
        
        # Truncate if needed
        if len(caption) > max_length:
            caption = caption[:max_length-3] + "..."
        
        # Platform-specific enhancements
        if platform == "instagram":
            # Ensure hashtags at end
            if not caption.endswith("\n\n"):
                caption += "\n\n"
        elif platform == "linkedin":
            # More professional tone
            pass
        elif platform == "x":
            # Concise
            pass
        
        return caption
```

### 4.6 Hashtag Engine

```python
# backend/app/ai/hashtag/engine.py

class HashtagEngine:
    """Hashtag extraction, analysis, and recommendation."""
    
    def __init__(self, config: HashtagConfig, model_registry: ModelRegistry):
        self.config = config
        self.model_registry = model_registry
    
    async def extract_hashtags(self, text: str) -> List[str]:
        """Extract and normalize hashtags."""
        tags = re.findall(r'#(\w+)', text.lower())
        return list(set(tags))  # Deduplicate
    
    async def analyze_performance(self, platform: str, 
                                 account_id: str,
                                 lookback_days: int = 90) -> HashtagPerformance:
        """Analyze historical hashtag performance."""
        
        posts = await self._get_posts_with_hashtags(account_id, platform, lookback_days)
        
        performance = {}
        for post in posts:
            for tag in post.hashtags:
                if tag not in performance:
                    performance[tag] = {"engagement": 0, "count": 0}
                performance[tag]["engagement"] += sum(post.engagement.values())
                performance[tag]["count"] += 1
        
        # Calculate average engagement per hashtag
        for tag, data in performance.items():
            data["avg_engagement"] = data["engagement"] / data["count"]
        
        # Top-K by performance
        sorted_tags = sorted(performance.items(), 
                           key=lambda x: x[1]["avg_engagement"], reverse=True)
        
        return HashtagPerformance(
            platform=platform,
            account_id=account_id,
            top_hashtags=[tag for tag, _ in sorted_tags[:self.config.top_k]],
            performance_data=performance
        )
    
    async def recommend_hashtags(self, content: UniversalContent, 
                                platform: str,
                                count: int = 10) -> HashtagRecommendation:
        """Recommend hashtags based on content and platform trends."""
        
        # 1. Content-based tags (from content analysis)
        content_tags = await self._extract_content_tags(content)
        
        # 2. Platform trending tags
        trending_tags = await self._get_trending_tags(platform, count)
        
        # 3. Account's historical best tags
        historical_tags = await self._get_account_best_tags(content.user_id, platform)
        
        # 4. Combine and rank
        all_candidates = set(content_tags + trending_tags + historical_tags)
        ranked = self._rank_hashtags(all_candidates, content, platform)
        
        return HashtagRecommendation(
            platform=platform,
            recommendations=ranked[:count],
            content_based=content_tags[:count//3],
            trending=trending_tags[:count//3],
            personalized=historical_tags[:count//3]
        )
```

### 4.7 Recommendation Engine (Central Intelligence)

```python
# backend/app/ai/recommendation/engine.py

class RecommendationEngine:
    """Central recommendation engine combining all AI modules."""
    
    def __init__(self, 
                 sentiment_engine: SentimentEngine,
                 scheduling_engine: SchedulingEngine,
                 growth_engine: GrowthEngine,
                 caption_engine: CaptionEngine,
                 hashtag_engine: HashtagEngine,
                 analytics_service: AnalyticsService,
                 model_registry: ModelRegistry):
        self.sentiment = sentiment_engine
        self.scheduling = scheduling_engine
        self.growth = growth_engine
        self.caption = caption_engine
        self.hashtag = hashtag_engine
        self.analytics = analytics_service
        self.model_registry = model_registry
    
    async def generate_recommendations(self, 
                                      user_id: str,
                                      content: UniversalContent,
                                      target_platforms: List[str]) -> List[Recommendation]:
        """Generate comprehensive AI recommendations."""
        
        recommendations = []
        
        # 1. Caption optimization
        for platform in target_platforms:
            caption_analysis = await self.caption.analyze_caption(
                content.caption or content.text, platform
            )
            if caption_analysis.suggestions:
                recommendations.append(Recommendation(
                    type="caption_optimization",
                    platform=platform,
                    title=f"Optimize caption for {platform}",
                    description=caption_analysis.suggestions[0],
                    confidence=caption_analysis.score,
                    priority="high" if caption_analysis.score < 0.7 else "medium",
                    actionable=True
                ))
        
        # 2. Hashtag recommendations
        hashtag_rec = await self.hashtag.recommend_hashtags(content, target_platforms[0])
        if hashtag_rec.recommendations:
            recommendations.append(Recommendation(
                type="hashtag_recommendation",
                platform=target_platforms[0],
                title="Add high-performing hashtags",
                description=f"Consider: {', '.join(hashtag_rec.recommendations[:5])}",
                confidence=0.85,
                priority="medium",
                actionable=True
            ))
        
        # 3. Scheduling recommendation
        for platform in target_platforms:
            schedule_rec = await self.scheduling.predict_optimal_time(
                platform, content.user_id, content
            )
            best_time = schedule_rec.recommendations[0][0]
            recommendations.append(Recommendation(
                type="scheduling",
                platform=platform,
                title=f"Optimal posting time for {platform}",
                description=f"Post at {best_time.strftime('%A %I:%M %p')} for highest engagement",
                confidence=schedule_rec.recommendations[0][1],
                priority="high",
                actionable=True
            ))
        
        # 4. Platform selection based on predicted engagement
        platform_predictions = {}
        for platform in target_platforms:
            pred = await self.growth.predict_growth(platform, content.user_id, 30)
            platform_predictions[platform] = pred.predicted_followers
        
        best_platform = max(platform_predictions, key=platform_predictions.get)
        recommendations.append(Recommendation(
            type="platform_priority",
            platform=best_platform,
            title=f"Prioritize {best_platform} for maximum growth",
            description=f"Predicted {platform_predictions[best_platform]} followers in 30 days",
            confidence=0.75,
            priority="high",
            actionable=True
        ))
        
        # 5. Sentiment-based recommendation
        pre_sentiment = await self.sentiment.analyze_pre_post(content)
        if pre_sentiment.label in ("negative", "very_negative"):
            recommendations.append(Recommendation(
                type="sentiment_warning",
                platform="all",
                title="Content sentiment is negative",
                description="Consider more positive framing to improve engagement",
                confidence=pre_sentiment.confidence,
                priority="high",
                actionable=True
            ))
        
        return sorted(recommendations, key=lambda r: r.priority_order, reverse=True)

class Recommendation:
    type: str
    platform: str
    title: str
    description: str
    confidence: float
    priority: str  # "high", "medium", "low"
    actionable: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def priority_order(self) -> int:
        return {"high": 3, "medium": 2, "low": 1}[self.priority]
```

---

## 5. Model Registry

```python
# backend/app/ai/registry/registry.py

class ModelRegistry:
    """Central model registry with versioning and deployment states."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def register(self, model: "MLModel") -> "MLModel":
        """Register new model version."""
        model.created_at = datetime.utcnow()
        self.db.add(model)
        await self.db.commit()
        return model
    
    async def get_model(self, name: str, version: str = "latest", 
                       status: str = "production") -> Optional["MLModel"]:
        """Get model by name, version, and status."""
        query = select(MLModel).where(
            MLModel.name == name,
            MLModel.status == status
        )
        if version != "latest":
            query = query.where(MLModel.version == version)
        else:
            query = query.order_by(desc(MLModel.created_at))
        
        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none()
    
    async def promote_to_production(self, name: str, version: str) -> bool:
        """Promote model to production, demote previous."""
        # Demote current production
        await self.db.execute(
            update(MLModel)
            .where(MLModel.name == name, MLModel.status == "production")
            .values(status="staging")
        )
        
        # Promote new version
        await self.db.execute(
            update(MLModel)
            .where(MLModel.name == name, MLModel.version == version)
            .values(status="production")
        )
        await self.db.commit()
        return True
    
    async def get_model_metrics(self, name: str, version: str) -> Dict:
        """Get model performance metrics."""
        model = await self.get_model(name, version)
        return model.metrics if model else {}

@dataclass
class MLModel:
    id: str
    name: str                    # e.g., "scheduling_instagram"
    version: str                 # e.g., "v20260115_1430"
    type: str                    # "scheduling", "sentiment", "growth", "reply", "caption", "hashtag"
    status: str                  # "development", "staging", "production", "deprecated"
    platform: Optional[str]      # Platform-specific or "universal"
    dataset_version: str
    feature_version: str
    hyperparameters: Dict
    metrics: Dict                # accuracy, r2, f1, etc.
    trained_at: datetime
    model_path: str              # Path to serialized model
    created_at: datetime
```

---

## 6. Model Training Pipeline

```python
# backend/app/ai/pipelines/training_pipeline.py

class TrainingPipeline:
    """End-to-end ML training pipeline."""
    
    def __init__(self, 
                 feature_store: FeatureStore,
                 model_registry: ModelRegistry,
                 db: AsyncSession):
        self.feature_store = feature_store
        self.model_registry = model_registry
        self.db = db
    
    async def train_model(self, config: TrainingConfig) -> MLModel:
        """Execute complete training pipeline."""
        
        # 1. Data validation
        dataset = await self._load_and_validate_data(config.dataset_version)
        
        # 2. Feature engineering
        X, y = self._engineer_features(dataset, config.feature_version)
        
        # 3. Train/validation split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 4. Model training
        model = self._train_model(config.model_type, X_train, y_train, config.hyperparameters)
        
        # 5. Validation
        metrics = self._evaluate_model(model, X_val, y_val, config.task_type)
        
        # 6. Model registration
        ml_model = MLModel(
            name=config.model_name,
            version=config.version,
            type=config.model_type,
            platform=config.platform,
            status="development",
            dataset_version=config.dataset_version,
            feature_version=config.feature_version,
            hyperparameters=config.hyperparameters,
            metrics=metrics,
            trained_at=datetime.utcnow(),
            model_path=await self._save_model(model, config.model_name, config.version)
        )
        
        await self.model_registry.register(ml_model)
        
        return ml_model
    
    def _train_model(self, model_type: str, X, y, hyperparams):
        """Train model based on type."""
        if model_type == "scheduling":
            rf = RandomForestClassifier(**hyperparams)
            xgb = XGBClassifier(**hyperparams)
            return EnsembleModel(rf=rf, xgb=xgb)
        elif model_type == "growth":
            return RandomForestRegressor(**hyperparams)
        elif model_type == "sentiment_knn":
            return KNeighborsClassifier(**hyperparams)
        elif model_type == "reply":
            return LogisticRegression(**hyperparams)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
```

---

## 7. Performance Monitoring & Drift Detection

```python
# backend/app/ai/monitoring/monitor.py

class ModelPerformanceMonitor:
    """Monitor model predictions vs actual outcomes."""
    
    def __init__(self, model_registry: ModelRegistry, db: AsyncSession):
        self.model_registry = model_registry
        self.db = db
    
    async def log_prediction(self, prediction: "ModelPrediction"):
        """Log prediction for later comparison."""
        self.db.add(prediction)
        await self.db.commit()
    
    async def log_actual(self, prediction_id: str, actual_value: float):
        """Log actual outcome for comparison."""
        await self.db.execute(
            update(ModelPrediction)
            .where(ModelPrediction.id == prediction_id)
            .values(actual_outcome=actual_value, resolved_at=datetime.utcnow())
        )
        await self.db.commit()
    
    async def calculate_performance(self, model_name: str, 
                                   since: datetime) -> PerformanceReport:
        """Calculate prediction accuracy since given time."""
        
        predictions = await self.db.execute(
            select(ModelPrediction)
            .where(
                ModelPrediction.model_name == model_name,
                ModelPrediction.predicted_at >= since,
                ModelPrediction.actual_outcome.isnot(None)
            )
        )
        
        preds = predictions.scalars().all()
        if not preds:
            return PerformanceReport(model_name=model_name, sample_size=0)
        
        # Regression metrics
        if preds[0].task_type == "regression":
            y_true = [p.actual_outcome for p in preds]
            y_pred = [p.predicted_value for p in preds]
            return PerformanceReport(
                model_name=model_name,
                sample_size=len(preds),
                r2=r2_score(y_true, y_pred),
                rmse=np.sqrt(mean_squared_error(y_true, y_pred)),
                mae=mean_absolute_error(y_true, y_pred)
            )
        
        # Classification metrics
        else:
            y_true = [p.actual_class for p in preds]
            y_pred = [p.predicted_class for p in preds]
            return PerformanceReport(
                model_name=model_name,
                sample_size=len(preds),
                accuracy=accuracy_score(y_true, y_pred),
                f1=f1_score(y_true, y_pred, average="weighted"),
                precision=precision_score(y_true, y_pred, average="weighted"),
                recall=recall_score(y_true, y_pred, average="weighted")
            )
    
    async def detect_drift(self, model_name: str, threshold: float = 0.1) -> DriftReport:
        """Detect performance drift."""
        
        recent = await self.calculate_performance(model_name, datetime.utcnow() - timedelta(days=7))
        historical = await self.calculate_performance(model_name, datetime.utcnow() - timedelta(days=90))
        
        if recent.sample_size < 10 or historical.sample_size < 10:
            return DriftReport(detected=False, reason="insufficient_data")
        
        # Compare key metric
        if recent.r2 and historical.r2:
            drift = historical.r2 - recent.r2
            return DriftReport(
                detected=drift > threshold,
                metric="r2",
                historical_value=historical.r2,
                recent_value=recent.r2,
                drift_magnitude=drift,
                recommendation="retrain" if drift > threshold else "monitor"
            )
        
        return DriftReport(detected=False)
```

---

## 8. Configuration

```yaml
# backend/app/config/model_config.yaml
models:
  scheduling:
    active_model: "random_forest_xgboost_voting"
    platform_specific: true
    ensemble_method: "hard_voting"
    candidates:
      - "random_forest"
      - "xgboost"
      - "lightgbm"
  
  sentiment:
    active_model: "vader_knn"
    pre_post_method: "vader_knn"
    post_post_method: "comment_aggregation"
    thresholds:
      very_positive: 0.50
      positive: 0.05
      neutral_low: -0.05
      negative: -0.50
      very_negative: -0.50
    knn_k: 5
  
  growth:
    active_model: "random_forest_regressor"
    platform_specific: true
    candidates:
      - "random_forest"
      - "xgboost"
      - "lstm"
  
  reply:
    active_model: "tfidf_logistic"
    tfidf:
      stop_words: "english"
      ngram_range: [1, 2]
      max_features: 10000
    logistic:
      multi_class: "multinomial"
      max_iter: 1000
    confidence_thresholds:
      auto_reply: 0.90
      requires_approval: 0.70
      manual: 0.70
  
  caption:
    platform_limits:
      instagram:
        caption_max_length: 2200
        hashtag_max_count: 30
      facebook:
        caption_max_length: 63206
        hashtag_max_count: 30
      x:
        caption_max_length: 280
        hashtag_max_count: 10
      linkedin:
        caption_max_length: 3000
        hashtag_max_count: 10
      youtube:
        caption_max_length: 5000
        hashtag_max_count: 15
  
  hashtag:
    top_k: 5
    min_frequency: 3
    trend_lookback_days: 7

# backend/app/config/sentiment_config.yaml
sentiment:
  thresholds:
    very_positive: 0.50
    positive: 0.05
    neutral_low: -0.05
    negative: -0.50
    very_negative: -0.50
  knn:
    k: 5
    enabled: true
  dual_phase:
    pre_post_weight: 0.4
    post_post_weight: 0.6
  temporal:
    window_days: 30
    min_samples: 5
```

---

## 9. Decision Records

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-019 | Normalized input for all AI engines | Platform independence, single feature store |
| ADR-020 | Dual-phase sentiment (VADER + k-NN) | Research baseline, proven accuracy |
| ADR-021 | Platform-specific scheduling models | Different optimal times per platform |
| ADR-022 | Platform-specific growth models | Research uses platform-specific R² |
| ADR-023 | ReplyEngine abstraction (TF-IDF/LLM/Hybrid) | Future LLM integration without rewrite |
| ADR-024 | Human-in-the-loop with confidence thresholds | Safe automation, user control |
| ADR-025 | Central RecommendationEngine | Single source of actionable insights |
| ADR-026 | Model registry with versioning | Reproducibility, A/B testing, rollback |
| ADR-027 | Training pipeline with feature versioning | Consistent feature engineering |
| ADR-028 | Performance monitoring + drift detection | Models degrade over time |
| ADR-029 | Mock data support for all engines | Testability without real platforms |

---

## 10. Research Baseline Preservation

| Engine | Research Baseline | Implementation |
|--------|------------------|----------------|
| **Scheduling** | RF + XGBoost + Hard Voting (88.08%) | EnsembleModel with hard voting |
| **Sentiment** | VADER + k-NN k=5 (89.00%, 0.019s) | PrePostAnalyzer with k-NN refinement |
| **Auto-Reply** | TF-IDF (1,2) + Logistic Regression (88.00%) | TFIDFReplyEngine with multinomial LR |
| **Growth (IG)** | RF Regressor (89.2% R²) | GrowthEngine per platform |
| **Growth (FB)** | RF Regressor (87.5% R²) | GrowthEngine per platform |
| **Growth (TW)** | RF Regressor (85.8% R²) | GrowthEngine per platform |
| **Caption/Hashtag** | Top-K=5 (92.70%) | HashtagEngine with Top-K evaluation |

---

**Status:** DESIGN — AWAITING APPROVAL  
**Next:** Upon approval, proceed to Phase 3 (Core Foundation) implementation.