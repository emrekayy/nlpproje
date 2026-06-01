import { IntelligenceScoreBreakdown } from "@/components/intelligence-score-breakdown";
import { Pill } from "@/components/pill";
import { SectionCard } from "@/components/section-card";
import {
  formatRecommendationVerdict,
  getBestForPersonas,
  getBuyingVerdictCopy,
  getCommunitySentimentLabel,
  getIntelligenceScoreBreakdown,
  getProductIntelligenceScore,
  getRecommendationTone,
  getRiskSignalLabel,
} from "@/lib/utils";
import type { ProductDetail } from "@/types/product";

type IntelligenceDashboardProps = {
  product: ProductDetail;
};

export function IntelligenceDashboard({ product }: IntelligenceDashboardProps) {
  const score = getProductIntelligenceScore(product);
  const scoreBreakdown = getIntelligenceScoreBreakdown(product, score);
  const personas = getBestForPersonas(product);
  const riskLabel = getRiskSignalLabel(product.common_issues);
  const sentimentLabel = getCommunitySentimentLabel(product.review_summary);

  return (
    <SectionCard
      title="Urun Zekasi Ozeti"
      description="Bu urune dair en kritik sinyaller tek bir bakista."
    >
      <div className="rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-soft sm:p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Skor dagilimi</p>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              Genel karar sinyalini olusturan ana boyutlar.
            </p>
          </div>
          <Pill
            label={formatRecommendationVerdict(product.decision_support.recommendation_verdict)}
            tone={getRecommendationTone(product.decision_support.recommendation_verdict)}
          />
        </div>
        <IntelligenceScoreBreakdown
          overallScore={scoreBreakdown.overallScore}
          metrics={scoreBreakdown.metrics}
          summary={getBuyingVerdictCopy(product)}
        />
      </div>

      {/* Sentiment + risk */}
      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.2fr),minmax(0,0.8fr)]">
        <div className="grid gap-4 sm:grid-cols-2">
          <article className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Topluluk hissi</p>
            <p className="mt-3 text-lg font-semibold tracking-tight text-slate-950">{sentimentLabel}</p>
            <p className="mt-1.5 text-sm leading-6 text-slate-500 line-clamp-2">
              {product.review_summary.overall_sentiment_summary}
            </p>
          </article>

          <article className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Risk profili</p>
            <p className="mt-3 text-lg font-semibold tracking-tight text-slate-950">{riskLabel}</p>
            <p className="mt-1.5 text-sm leading-6 text-slate-500">
              {product.common_issues.length > 0
                ? `${product.common_issues.length} tekrar eden sorun tespit edildi.`
                : "Onemli tekrar eden sorun tespit edilmedi."}
            </p>
          </article>
        </div>

        {/* Persona + sayisal ozet */}
        <div className="grid gap-4">
          <article className="rounded-[1.75rem] border border-slate-200 bg-white p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Bu urune uygun kullanici profili</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {personas.length > 0 ? (
                personas.map((persona) => <Pill key={persona} label={persona} tone="neutral" />)
              ) : (
                <p className="text-sm text-slate-400">Belirgin kullanici profili sinyali bulunamadi.</p>
              )}
            </div>
          </article>

          <article className="rounded-[1.75rem] border border-slate-200 bg-white p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Analiz ozeti</p>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {[
                { label: "Guclu yan", value: product.review_summary.top_positive_aspects.length },
                { label: "Sorun", value: product.common_issues.length },
                { label: "Kanit", value: product.review_summary.evidence_snippets.length },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-center">
                  <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">{label}</p>
                  <p className="mt-2 text-2xl font-semibold tabular-nums text-slate-950">{value}</p>
                </div>
              ))}
            </div>
          </article>
        </div>
      </div>
    </SectionCard>
  );
}
