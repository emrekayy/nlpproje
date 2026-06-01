export type EvidenceSnippet = {
  source: string;
  text: string;
  similarity_score?: number | null;
  chunk_type?: string | null;
  aspect?: string | null;
  source_type?: string | null;
  source_platform?: string | null;
  verified_purchase?: boolean | null;
  rating?: number | null;
  review_title?: string | null;
  source_url?: string | null;
};

export type CommunityReview = {
  id: string;
  model: string;
  rating: number;
  text: string;
  aspect: string;
  sentiment: "positive" | "neutral" | "negative";
  source: string;
  timestamp: string;
};

export type AspectFrequency = {
  aspect: string;
  count: number;
};

export type IssueItem = {
  title: string;
  description: string;
  confidence_score: number;
};

export type ReviewSummary = {
  overall_sentiment_summary: string;
  top_positive_aspects: string[];
  top_negative_aspects: string[];
  evidence_snippets: EvidenceSnippet[];
  chatbot_ready_summary: string;
};

export type ProductDecisionSupport = {
  recommendation_verdict: string;
  quick_verdict: string;
  best_for: string[];
  not_ideal_for: string[];
};

export type ProductAnalytics = {
  review_count: number;
  average_rating: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
  top_issues: string[];
  top_strengths: string[];
  issue_frequency: AspectFrequency[];
  recommendation_score: number;
  source_summary: string[];
  community_sentiment: string;
};

export type Product = {
  id: string;
  slug: string;
  name: string;
  family: string;
  release_year: number;
  chipset: string;
  display_type: string;
  display_size: string;
  battery_summary: string;
  camera_summary: string;
  storage_options: string[];
  weight: string;
  notable_highlights: string[];
  short_description: string;
  // Intelligence fields derived from review analytics
  strengths: string[];
  weaknesses: string[];
  risk_signals: string[];
  issue_patterns: string[];
  community_sentiment: string;
  review_count: number;
  average_rating: number;
  recommendation_score: number;
  target_users: string[];
  source_summary: string[];
  user_quotes: string[];
};

export type ProductListResponse = {
  items: Product[];
  total: number;
};

export type ProductDetail = Product & {
  review_summary: ReviewSummary;
  common_issues: IssueItem[];
  decision_support: ProductDecisionSupport;
  analytics: ProductAnalytics;
};

export type ProductSummaryResponse = {
  slug: string;
  name: string;
  review_summary: ReviewSummary;
};

export type ProductIssuesResponse = {
  slug: string;
  name: string;
  common_issues: IssueItem[];
  evidence_snippets: EvidenceSnippet[];
};

export type ProductReviewsResponse = {
  slug: string;
  name: string;
  total: number;
  items: CommunityReview[];
};

export type NormalizedRealReview = {
  id: string;
  model: string;
  source: string;
  rating: number | null;
  review_text: string;
  review_title?: string | null;
  date?: string | null;
  country?: string | null;
  verified_purchase?: boolean | null;
  sentiment?: string | null;
  aspect?: string | null;
  source_url?: string | null;
};

export type CountBreakdownItem = {
  label: string;
  count: number;
};

export type RealProductReviewsResponse = {
  slug: string;
  name: string;
  total: number;
  items: NormalizedRealReview[];
};

export type RealReviewStatsResponse = {
  slug: string;
  name: string;
  total_reviews: number;
  average_rating: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  source_distribution: CountBreakdownItem[];
  rating_distribution: CountBreakdownItem[];
  verified_review_count: number;
  top_aspects: AspectFrequency[];
};

export type SemanticSearchHit = {
  review_id: string;
  slug: string | null;
  model: string;
  rating: number | null;
  text: string;
  aspect: string;
  sentiment: "positive" | "neutral" | "negative" | string;
  source: string;
  timestamp: string | null;
  similarity_score: number;
  chunk_type?: string | null;
  chunk_label?: string | null;
};

export type SemanticSearchResponse = {
  query: string;
  total: number;
  items: SemanticSearchHit[];
};

export type ChatRequest = {
  slug: string;
  question: string;
  history?: Array<Record<string, unknown>>;
};

export type ChatResponse = {
  answer: string;
  quick_verdict: string;
  strengths: string[];
  weaknesses: string[];
  issue_warnings: string[];
  recommendation_score: number;
  evidence_snippets: EvidenceSnippet[];
  recommendation_verdict: string;
  confidence_score: number;
  confidence_label?: string | null;
  evidence_count: number;
  top_retrieved_sources: string[];
  intent_category?: string | null;
  retrieval_debug?: Array<Record<string, unknown>>;
};
