from typing import Any

from pydantic import BaseModel, Field


class EvidenceSnippet(BaseModel):
    source: str
    text: str
    similarity_score: float | None = None
    chunk_type: str | None = None
    aspect: str | None = None
    source_type: str | None = None
    source_platform: str | None = None
    verified_purchase: bool | None = None
    rating: float | None = None
    review_title: str | None = None
    source_url: str | None = None


class CommunityReview(BaseModel):
    id: str
    model: str
    rating: int = Field(ge=1, le=5)
    text: str
    aspect: str
    sentiment: str
    source: str
    timestamp: str


class AspectFrequency(BaseModel):
    aspect: str
    count: int


class CountBreakdownItem(BaseModel):
    label: str
    count: int


class IssueItem(BaseModel):
    title: str
    description: str
    confidence_score: float = Field(ge=0, le=1)


class ReviewSummary(BaseModel):
    overall_sentiment_summary: str
    top_positive_aspects: list[str]
    top_negative_aspects: list[str]
    evidence_snippets: list[EvidenceSnippet]
    chatbot_ready_summary: str


class ProductDecisionSupport(BaseModel):
    recommendation_verdict: str
    quick_verdict: str
    best_for: list[str]
    not_ideal_for: list[str]


class ProductAnalytics(BaseModel):
    review_count: int
    average_rating: float
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    top_issues: list[str]
    top_strengths: list[str]
    issue_frequency: list[AspectFrequency]
    recommendation_score: int = Field(ge=0, le=100)
    source_summary: list[str]
    community_sentiment: str


class ProductBase(BaseModel):
    id: str
    slug: str
    name: str
    family: str
    release_year: int
    chipset: str
    display_type: str
    display_size: str
    battery_summary: str
    camera_summary: str
    storage_options: list[str]
    weight: str
    notable_highlights: list[str]
    short_description: str
    # Intelligence fields — derived from review analytics
    strengths: list[str]
    weaknesses: list[str]
    risk_signals: list[str]
    issue_patterns: list[str]
    community_sentiment: str
    review_count: int
    average_rating: float
    recommendation_score: int = Field(ge=0, le=100)
    target_users: list[str]
    source_summary: list[str]
    user_quotes: list[str]


class ProductSummaryResponse(BaseModel):
    slug: str
    name: str
    review_summary: ReviewSummary


class ProductIssuesResponse(BaseModel):
    slug: str
    name: str
    common_issues: list[IssueItem]
    evidence_snippets: list[EvidenceSnippet]


class ProductDetailResponse(ProductBase):
    review_summary: ReviewSummary
    common_issues: list[IssueItem]
    decision_support: ProductDecisionSupport
    analytics: ProductAnalytics


class ProductListResponse(BaseModel):
    items: list[ProductBase]
    total: int


class ChatRequest(BaseModel):
    slug: str
    question: str
    history: list[dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    quick_verdict: str
    strengths: list[str]
    weaknesses: list[str]
    issue_warnings: list[str]
    recommendation_score: int = Field(ge=0, le=100)
    evidence_snippets: list[EvidenceSnippet]
    recommendation_verdict: str
    confidence_score: int = Field(ge=0, le=100)
    confidence_label: str | None = None
    evidence_count: int = Field(ge=0)
    top_retrieved_sources: list[str]
    intent_category: str | None = None
    retrieval_debug: list[dict[str, Any]] = Field(default_factory=list)


class ProductReviewsResponse(BaseModel):
    slug: str
    name: str
    total: int
    items: list[CommunityReview]


class NormalizedRealReview(BaseModel):
    id: str
    model: str
    source: str
    rating: float | None = None
    review_text: str
    review_title: str | None = None
    date: str | None = None
    country: str | None = None
    verified_purchase: bool | None = None
    sentiment: str | None = None
    aspect: str | None = None
    source_url: str | None = None


class RealProductReviewsResponse(BaseModel):
    slug: str
    name: str
    total: int
    items: list[NormalizedRealReview]


class RealReviewStatsResponse(BaseModel):
    slug: str
    name: str
    total_reviews: int
    average_rating: float
    positive_count: int
    neutral_count: int
    negative_count: int
    source_distribution: list[CountBreakdownItem]
    rating_distribution: list[CountBreakdownItem]
    verified_review_count: int
    top_aspects: list[AspectFrequency]


class SemanticSearchHit(BaseModel):
    review_id: str
    slug: str | None = None
    model: str
    rating: int | None = Field(default=None, ge=1, le=5)
    text: str
    aspect: str
    sentiment: str
    source: str
    timestamp: str | None = None
    similarity_score: float
    chunk_type: str | None = None
    chunk_label: str | None = None


class SemanticSearchResponse(BaseModel):
    query: str
    total: int
    items: list[SemanticSearchHit]
