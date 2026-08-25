from app.core.normalization import ContentNormalizer, MetricNormalizer, NormalizedContent, NormalizedMetric


def test_content_normalizer_extracts_hashtags_mentions_and_links():
    raw = {
        "text": "AI is changing marketing #growth #marketing @team check https://example.com",
        "caption": "Launch day",
        "content_type": "image",
        "location": "New York",
        "language": "en"
    }

    normalized = ContentNormalizer.normalize_content(raw)

    assert isinstance(normalized, NormalizedContent)
    assert normalized.text == "AI is changing marketing #growth #marketing @team check https://example.com"
    assert normalized.hashtags == ["growth", "marketing"]
    assert normalized.mentions == ["team"]
    assert normalized.links == ["https://example.com"]
    assert normalized.content_type == "image"
    assert normalized.location == "New York"
    assert normalized.language == "en"


def test_metric_normalizer_maps_platform_metrics_to_common_types():
    instagram_like = MetricNormalizer.normalize_metric({
        "metric_type": "like_count",
        "value": 150,
        "source_platform": "instagram",
        "original_metric": "like_count",
    })

    x_share = MetricNormalizer.normalize_metric({
        "metric_type": "retweet_count",
        "value": 42,
        "source_platform": "x",
        "original_metric": "retweet_count",
    })

    youtube_view = MetricNormalizer.normalize_metric({
        "metric_type": "view_count",
        "value": 5000,
        "source_platform": "youtube",
        "original_metric": "view_count",
    })

    assert isinstance(instagram_like, NormalizedMetric)
    assert instagram_like.metric_type == "LIKE"
    assert x_share.metric_type == "SHARE"
    assert youtube_view.metric_type == "VIEW"
    assert instagram_like.value == 150
    assert x_share.source_platform == "x"
