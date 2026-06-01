import Link from "next/link";
import { notFound } from "next/navigation";

import { ChatbotPanel } from "@/features/chatbot/chatbot-panel";
import { EvidenceSnippetsSection } from "@/features/evidence/evidence-snippets-section";
import { DecisionSupportCard } from "@/features/product-detail/decision-support-card";
import { IntelligenceDashboard } from "@/features/product-detail/intelligence-dashboard";
import { ProductHero } from "@/features/product-detail/product-hero";
import { ProductOverview } from "@/features/product-detail/product-overview";
import { IssuesSection } from "@/features/issues/issues-section";
import { ReviewSummaryCard } from "@/features/review-summary/review-summary-card";
import { getProductDetail } from "@/services/product-service";

type ProductDetailPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  const { slug } = await params;

  try {
    const product = await getProductDetail(slug);

    return (
      <main className="space-y-6 lg:space-y-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:border-slate-300 hover:text-slate-950"
        >
          <span aria-hidden="true">←</span>
          Tum modeller
        </Link>

        <ProductHero product={product} reviewSummary={product.review_summary} />
        <IntelligenceDashboard product={product} />

        <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1.7fr),minmax(320px,0.9fr)] xl:gap-7">
          <div className="space-y-5 lg:space-y-6">
            <DecisionSupportCard decisionSupport={product.decision_support} />
            <ProductOverview product={product} />
            <ReviewSummaryCard summary={product.review_summary} />
            <IssuesSection issues={product.common_issues} />
            <EvidenceSnippetsSection evidence={product.review_summary.evidence_snippets} />
          </div>

          <aside className="space-y-5">
            <ChatbotPanel
              product={product}
              slug={product.slug}
              name={product.name}
              summary={product.review_summary.chatbot_ready_summary}
              recommendationVerdict={product.decision_support.recommendation_verdict}
            />
          </aside>
        </div>
      </main>
    );
  } catch {
    notFound();
  }
}
