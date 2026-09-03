"""AI Content Engine API router."""

from fastapi import APIRouter, Depends

from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.ai.content_engine import AIContentEngine
from backend.app.ai.sentiment import SentimentEngine
from backend.app.ai.caption import CaptionEngine
from backend.app.ai.hashtag import HashtagEngine
from backend.app.core.schemas.ai import (
    SentimentAnalyzeRequest,
    SentimentAnalyzeResponse,
    PostSentimentRequest,
    CaptionAnalyzeRequest,
    CaptionAnalyzeResponse,
    CaptionFeaturesResponse,
    CaptionOptimizeRequest,
    CaptionOptimizeResponse,
    HashtagRecommendRequest,
    HashtagRecommendResponse,
    HashtagItem,
    ContentOptimizeAllRequest,
    ContentOptimizeAllResponse,
    PlatformVariantItem,
)

router = APIRouter(prefix="/ai", tags=["AI Content Engine"])

ai_engine = AIContentEngine()


@router.post("/sentiment/analyze", response_model=SentimentAnalyzeResponse)
async def analyze_pre_posting_sentiment(
    request: SentimentAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze sentiment of drafted text before publication (Phase 1)."""
    res = ai_engine.sentiment.analyze_pre_posting(request.text)
    return SentimentAnalyzeResponse(
        score=res.score,
        label=res.label,
        confidence=res.confidence,
        positive_score=res.positive_score,
        neutral_score=res.neutral_score,
        negative_score=res.negative_score,
        details=res.details,
    )


@router.post("/sentiment/comments", response_model=SentimentAnalyzeResponse)
async def analyze_post_comments_sentiment(
    request: PostSentimentRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze and aggregate audience sentiment across post comments (Phase 2)."""
    res = ai_engine.sentiment.analyze_post_posting(request.comments)
    return SentimentAnalyzeResponse(
        score=res.score,
        label=res.label,
        confidence=res.confidence,
        positive_score=res.positive_score,
        neutral_score=res.neutral_score,
        negative_score=res.negative_score,
        details=res.details,
    )


@router.post("/caption/analyze", response_model=CaptionAnalyzeResponse)
async def analyze_caption_quality(
    request: CaptionAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """Evaluate caption quality score, readability, CTA, hooks, and suggestions."""
    res = ai_engine.caption.analyze(request.text, platform=request.platform)
    f = res.features
    return CaptionAnalyzeResponse(
        score=res.score,
        grade=res.grade,
        features=CaptionFeaturesResponse(
            length=f.length,
            word_count=f.word_count,
            hashtag_count=f.hashtag_count,
            mention_count=f.mention_count,
            emoji_count=f.emoji_count,
            question_count=f.question_count,
            exclamation_count=f.exclamation_count,
            has_cta=f.has_cta,
            detected_cta=f.detected_cta,
        ),
        strengths=res.strengths,
        suggestions=res.suggestions,
    )


@router.post("/caption/optimize", response_model=CaptionOptimizeResponse)
async def optimize_caption_for_platform(
    request: CaptionOptimizeRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate platform-adapted caption variant."""
    optimized = ai_engine.caption.optimize_for_platform(
        request.text,
        platform=request.platform,
        target_tone=request.target_tone,
    )
    return CaptionOptimizeResponse(
        original_text=request.text,
        optimized_text=optimized,
        platform=request.platform,
        character_count=len(optimized),
    )


@router.post("/hashtags/recommend", response_model=HashtagRecommendResponse)
async def recommend_hashtags(
    request: HashtagRecommendRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate Top-K hashtag recommendations based on content keywords."""
    res = ai_engine.hashtag.recommend_hashtags(
        request.text,
        platform=request.platform,
        top_k=request.top_k,
    )
    return HashtagRecommendResponse(
        top_k=res.top_k,
        recommendations=[
            HashtagItem(
                hashtag=r.hashtag,
                category=r.category,
                relevance_score=r.relevance_score,
                is_trending=r.is_trending,
            )
            for r in res.recommendations
        ],
        platform=res.platform,
        max_recommended=res.max_recommended,
    )


@router.post("/content/optimize-all", response_model=ContentOptimizeAllResponse)
async def optimize_content_all(
    request: ContentOptimizeAllRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute unified multi-model AI content optimization across all platforms."""
    res = ai_engine.optimize(
        request.text,
        platforms=request.platforms,
        top_k_hashtags=request.top_k_hashtags,
    )

    f = res.caption_analysis.features
    return ContentOptimizeAllResponse(
        sentiment=SentimentAnalyzeResponse(
            score=res.sentiment.score,
            label=res.sentiment.label,
            confidence=res.sentiment.confidence,
            positive_score=res.sentiment.positive_score,
            neutral_score=res.sentiment.neutral_score,
            negative_score=res.sentiment.negative_score,
            details=res.sentiment.details,
        ),
        caption_analysis=CaptionAnalyzeResponse(
            score=res.caption_analysis.score,
            grade=res.caption_analysis.grade,
            features=CaptionFeaturesResponse(
                length=f.length,
                word_count=f.word_count,
                hashtag_count=f.hashtag_count,
                mention_count=f.mention_count,
                emoji_count=f.emoji_count,
                question_count=f.question_count,
                exclamation_count=f.exclamation_count,
                has_cta=f.has_cta,
                detected_cta=f.detected_cta,
            ),
            strengths=res.caption_analysis.strengths,
            suggestions=res.caption_analysis.suggestions,
        ),
        hashtags=HashtagRecommendResponse(
            top_k=res.hashtags.top_k,
            recommendations=[
                HashtagItem(
                    hashtag=r.hashtag,
                    category=r.category,
                    relevance_score=r.relevance_score,
                    is_trending=r.is_trending,
                )
                for r in res.hashtags.recommendations
            ],
            platform=res.hashtags.platform,
            max_recommended=res.hashtags.max_recommended,
        ),
        platform_variants={
            k: PlatformVariantItem(
                platform=v.platform,
                text=v.text,
                recommended_hashtags=v.recommended_hashtags,
                character_count=v.character_count,
            )
            for k, v in res.platform_variants.items()
        },
    )
