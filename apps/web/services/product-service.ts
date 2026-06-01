import { apiFetch } from "@/services/api-client";
import type {
  ChatRequest,
  ChatResponse,
  ProductDetail,
  ProductAnalytics,
  ProductIssuesResponse,
  ProductListResponse,
  ProductReviewsResponse,
  RealProductReviewsResponse,
  RealReviewStatsResponse,
  SemanticSearchResponse,
  ProductSummaryResponse
} from "@/types/product";

export function getProducts() {
  return apiFetch<ProductListResponse>("/api/products");
}

export function getProductDetail(slug: string) {
  return apiFetch<ProductDetail>(`/api/products/${slug}`);
}

export function getProductSummary(slug: string) {
  return apiFetch<ProductSummaryResponse>(`/api/products/${slug}/summary`);
}

export function getProductIssues(slug: string) {
  return apiFetch<ProductIssuesResponse>(`/api/products/${slug}/issues`);
}

export function getProductReviews(identifier: string) {
  return apiFetch<ProductReviewsResponse>(`/api/reviews/${identifier}`);
}

export function getRealProductReviews(identifier: string) {
  return apiFetch<RealProductReviewsResponse>(`/api/reviews/real/${identifier}`);
}

export function getRealProductReviewStats(identifier: string) {
  return apiFetch<RealReviewStatsResponse>(`/api/reviews/real/${identifier}/stats`);
}

export function getProductAnalytics(identifier: string) {
  return apiFetch<ProductAnalytics>(`/api/analytics/${identifier}`);
}

export function searchSemanticReviews(query: string, limit = 8) {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit)
  });

  return apiFetch<SemanticSearchResponse>(`/api/search/semantic?${params.toString()}`);
}

export function sendChatMessage(payload: ChatRequest) {
  return apiFetch<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
