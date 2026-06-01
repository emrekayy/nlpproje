"use client";

import { type FormEvent, useState } from "react";

import { IntelligenceScoreBreakdown } from "@/components/intelligence-score-breakdown";
import { Pill } from "@/components/pill";
import { SectionCard } from "@/components/section-card";
import {
  cn,
  formatRecommendationVerdict,
  getIntelligenceScoreBreakdown,
  getRecommendationTone,
  getScoreColor,
} from "@/lib/utils";
import { sendChatMessage } from "@/services/product-service";
import type { ChatResponse, EvidenceSnippet, ProductDetail } from "@/types/product";

type ChatbotPanelProps = {
  product: ProductDetail;
  slug: string;
  name: string;
  summary: string;
  recommendationVerdict: string;
};

const QUICK_QUESTIONS = [
  "2026'da alinmaya deger mi?",
  "En sik sikayet edilen sorunlar neler?",
  "Ogrenci kullanimi icin mantikli mi?",
  "Pil omru guvenilir mi?",
  "Onceki nesle gore fark nedir?",
];

function AssistantAvatar() {
  return (
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-[11px] font-semibold uppercase tracking-[0.2em] text-white shadow-soft">
      AI
    </div>
  );
}

function UserAvatar() {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 shadow-sm">
      You
    </div>
  );
}

function DataCredibilityCard() {
  const sources = ["Reddit", "Community forums", "User reviews", "Tech communities"];

  return (
    <div className="rounded-[1.75rem] border border-slate-200 bg-slate-50/80 p-4 shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.35)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Veri guvenilirligi</p>
          <p className="mt-1.5 text-sm leading-6 text-slate-500">
            Model sinyalleri farkli topluluk katmanlariyla capraz okunur.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-right shadow-sm">
          <p className="text-[10px] uppercase tracking-[0.16em] text-slate-400">Incelenen yorum</p>
          <p className="mt-1 text-xl font-semibold tracking-tight text-slate-950">12,431</p>
        </div>
      </div>

      <div className="mt-4 rounded-[1.25rem] border border-slate-200 bg-white p-4">
        <p className="text-[11px] uppercase tracking-[0.16em] text-slate-400">Kaynaklar</p>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {sources.map((source) => (
            <li key={source} className="flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">
              <span aria-hidden="true" className="text-emerald-500">
                ✓
              </span>
              <span>{source}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function getEvidenceSourceMeta(source: string) {
  const normalized = source.toLowerCase();

  if (normalized.includes("amazon")) {
    return { icon: "🟠", label: "Amazon Reviews" };
  }
  if (normalized.includes("flipkart")) {
    return { icon: "🟡", label: "Flipkart Reviews" };
  }
  if (normalized.includes("apple review dataset")) {
    return { icon: "🔵", label: "Apple Review Dataset" };
  }
  if (normalized.includes("legacy")) {
    return { icon: "⚪", label: "Legacy Review Dataset" };
  }
  if (normalized.includes("reddit")) {
    return { icon: "🟠", label: "Reddit" };
  }
  if (normalized.includes("gsm")) {
    return { icon: "🟢", label: "GSM Arena" };
  }
  if (normalized.includes("forum")) {
    return { icon: "🟢", label: "Community forum" };
  }
  if (normalized.includes("user review") || normalized.includes("review")) {
    return { icon: "🔵", label: "User review" };
  }
  if (normalized.includes("tech")) {
    return { icon: "🟣", label: "Tech community" };
  }
  if (normalized.includes("summary")) {
    return { icon: "⚪", label: source };
  }

  return { icon: "🟢", label: source };
}

function getEvidenceConfidence(similarityScore?: number | null) {
  if (similarityScore == null) return { label: "Context", tone: "neutral" as const };
  if (similarityScore >= 0.78) return { label: "High", tone: "positive" as const };
  if (similarityScore >= 0.62) return { label: "Medium", tone: "warning" as const };
  return { label: "Low", tone: "neutral" as const };
}

function getEvidenceCategory(snippet: EvidenceSnippet) {
  const aspect = snippet.aspect ?? "";
  const chunkType = snippet.chunk_type ?? "";

  if (aspect === "heat") return "Gaming / Heating";
  if (aspect === "battery") return "Battery";
  if (aspect === "camera") return "Camera";
  if (aspect === "performance") return "Gaming / Performance";
  if (chunkType === "community_opinion" || chunkType === "user_evidence") return "Community";
  if (chunkType === "product_description") return "Product";
  if (chunkType === "risk_signal") return "Risk";

  return "General";
}

function EvidenceCards({ items }: { items: EvidenceSnippet[] }) {
  return (
    <div className="mt-5 rounded-[1.5rem] border border-slate-200 bg-slate-50/70 p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.16em] text-slate-400">Dayandigi kaynaklar</p>
          <p className="mt-1 text-sm text-slate-500">Yanitin dayandigi en guclu kanit parcalari.</p>
        </div>
        <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
          {Math.min(items.length, 3)} kart
        </span>
      </div>
      <ul className="mt-3 grid gap-3">
        {items.slice(0, 3).map((snippet, index) => {
          const sourceMeta = getEvidenceSourceMeta(snippet.source);
          const confidence = getEvidenceConfidence(snippet.similarity_score);
          const category = getEvidenceCategory(snippet);
          const platform = snippet.source_platform ?? snippet.source;
          const sourceType = snippet.source_type;
          const ratingLabel =
            typeof snippet.rating === "number" ? `${snippet.rating.toFixed(1).replace(".0", "")}/5` : null;
          const verifiedLabel =
            snippet.verified_purchase == null ? null : snippet.verified_purchase ? "Verified: Yes" : "Verified: No";

          return (
            <li
              key={`${snippet.source}-${index}`}
              className="rounded-[1.35rem] border border-slate-200 bg-slate-50/80 p-4 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:shadow-soft"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span aria-hidden="true" className="text-base">
                    {sourceMeta.icon}
                  </span>
                  <p className="text-sm font-semibold text-slate-900">{sourceMeta.label}</p>
                </div>
                <Pill label={confidence.label} tone={confidence.tone} />
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-700">"{snippet.text}"</p>

              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-3">
                {sourceType ? (
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
                    {sourceType}
                  </span>
                ) : null}
                {platform && platform !== sourceType ? (
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
                    {platform}
                  </span>
                ) : null}
                {verifiedLabel ? (
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
                    {verifiedLabel}
                  </span>
                ) : null}
                {ratingLabel ? (
                  <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
                    Rating: {ratingLabel}
                  </span>
                ) : null}
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium tracking-[0.02em] text-slate-600">
                  {category}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function ChatbotPanel({
  product,
  slug,
  name,
  summary,
  recommendationVerdict,
}: ChatbotPanelProps) {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState<string | null>(null);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitQuestion(nextQuestion: string) {
    const trimmed = nextQuestion.trim();
    if (!trimmed) return;

    setIsLoading(true);
    setError(null);
    setResponse(null);
    setSubmittedQuestion(trimmed);

    try {
      const result = await sendChatMessage({ slug, question: trimmed });
      setResponse(result);
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Yanit alinamadi."
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitQuestion(question);
  }

  const scoreColor = response ? getScoreColor(response.recommendation_score) : null;
  const scoreBreakdown = response
    ? getIntelligenceScoreBreakdown(product, response.recommendation_score)
    : null;

  return (
    <SectionCard
      title="AI Asistan"
      description="Katalog verileri ve topluluk sinyallerine dayali, satin alma kararini netlestiren yanitlar."
      className="xl:sticky xl:top-6"
    >
      <div className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4 shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.35)]">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Secili model</p>
            <p className="mt-1.5 truncate text-base font-semibold tracking-tight text-slate-950">{name}</p>
          </div>
          <Pill
            label={formatRecommendationVerdict(recommendationVerdict)}
            tone={getRecommendationTone(recommendationVerdict)}
          />
        </div>
        {!submittedQuestion && (
          <p className="mt-3 text-sm leading-6 text-slate-500">{summary}</p>
        )}
      </div>

      <div className="mt-5">
        <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Hizli sorular</p>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {QUICK_QUESTIONS.map((item, index) => (
            <button
              key={item}
              type="button"
              disabled={isLoading}
              onClick={() => {
                setQuestion(item);
                void submitQuestion(item);
              }}
              className={cn(
                "rounded-[1.1rem] border border-slate-200 bg-white px-3 py-2.5 text-left text-xs leading-[1.55] text-slate-600 shadow-sm transition duration-300",
                "hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 hover:shadow-soft disabled:cursor-not-allowed disabled:opacity-50",
                index === QUICK_QUESTIONS.length - 1 && QUICK_QUESTIONS.length % 2 !== 0
                  ? "col-span-2"
                  : ""
              )}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {/* Serbest soru alani */}
      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={3}
          placeholder="Kendi sorunuzu yazin..."
          className="w-full resize-none rounded-[1.35rem] border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition duration-300 placeholder:text-slate-400 focus:border-slate-400 focus:bg-white focus:ring-2 focus:ring-slate-200"
        />
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs leading-5 text-slate-400">Yanitlar urun verisi ve topluluk sinyallerine dayanir.</p>
          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className="shrink-0 rounded-full bg-slate-950 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition duration-300 hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            {isLoading ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Analiz ediliyor
              </span>
            ) : (
              "Gonder"
            )}
          </button>
        </div>
      </form>

      {/* Hata mesaji */}
      {error && (
        <div className="mt-4 rounded-[1.25rem] border border-rose-100 bg-rose-50 px-4 py-3">
          <p className="text-sm text-rose-700">{error}</p>
        </div>
      )}

      <div className="mt-6 rounded-[1.75rem] border border-slate-200 bg-slate-50/60 p-4 sm:p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Sohbet</p>
          <p className="text-xs text-slate-400">Grounded AI panel</p>
        </div>

        {!submittedQuestion && !isLoading && (
          <div className="rounded-[1.75rem] border border-dashed border-slate-300 bg-white/60 p-5">
            <p className="text-sm font-medium text-slate-700">Hazir sorulardan biriyle baslayin.</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Ornek: &ldquo;Uzun sureli kullanim icin bu model mantikli mi?&rdquo;
            </p>
          </div>
        )}

        {submittedQuestion && (
          <div className="flex justify-end">
            <div className="flex max-w-[92%] items-end gap-3">
              <div className="rounded-[1.5rem] rounded-br-md bg-slate-950 px-4 py-3 text-sm leading-6 text-white shadow-panel">
                {submittedQuestion}
              </div>
              <UserAvatar />
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex items-start gap-3">
            <AssistantAvatar />
            <div className="min-w-0 flex-1 overflow-hidden rounded-[1.75rem] rounded-bl-md border border-slate-200 bg-white shadow-soft">
              <div className="h-0.5 w-full animate-pulse bg-slate-200" />
              <div className="p-4 sm:p-5">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Asistan</p>
                <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-500">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-slate-400" />
                  Analiz hazirlaniyor
                </div>
                <div className="mt-4 space-y-2.5">
                  <div className="h-3 w-3/4 animate-pulse rounded-full bg-slate-100" />
                  <div className="h-3 w-full animate-pulse rounded-full bg-slate-100" />
                  <div className="h-3 w-5/6 animate-pulse rounded-full bg-slate-100" />
                </div>
                <div className="mt-4 grid gap-2">
                  <div className="h-24 animate-pulse rounded-[1.25rem] bg-slate-50" />
                  <div className="h-20 animate-pulse rounded-[1.25rem] bg-slate-50" />
                </div>
              </div>
            </div>
          </div>
        )}

        {response && !isLoading && scoreColor && scoreBreakdown && (
          <div className="flex items-start gap-3">
            <AssistantAvatar />
            <div className="min-w-0 flex-1 overflow-hidden rounded-[1.75rem] rounded-bl-md border border-slate-200 bg-white shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_24px_60px_-34px_rgba(15,23,42,0.35)]">
              <div className={cn("h-0.5 w-full", scoreColor.stripe)} />

              <div className="p-4 sm:p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Asistan</p>
                    <p className="mt-1 text-sm text-slate-500">Veriye dayali satin alma yorumu</p>
                  </div>
                  <Pill
                    label={formatRecommendationVerdict(response.recommendation_verdict)}
                    tone={getRecommendationTone(response.recommendation_verdict)}
                  />
                </div>

                <div className="mt-4 space-y-3">
                  {response.answer
                    .split("\n")
                    .map((paragraph) => paragraph.trim())
                    .filter(Boolean)
                    .map((paragraph, index) => (
                      <p key={`${index}-${paragraph.slice(0, 20)}`} className="text-sm leading-7 text-slate-700">
                        {paragraph}
                      </p>
                    ))}
                </div>

                {response.evidence_snippets.length > 0 && (
                  <EvidenceCards items={response.evidence_snippets} />
                )}

                <div className="mt-4 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-2">
                  <div className="rounded-[1.25rem] border border-slate-200 bg-slate-50 p-4">
                    <p className="text-[11px] uppercase tracking-[0.16em] text-slate-400">Hizli karar</p>
                    <p className="mt-2 text-sm leading-6 text-slate-700">{response.quick_verdict}</p>
                  </div>
                  <div className="rounded-[1.25rem] border border-slate-200 bg-slate-50 p-4">
                    <p className="text-[11px] uppercase tracking-[0.16em] text-slate-400">Yanit zemini</p>
                    <p className="mt-2 text-sm leading-6 text-slate-700">
                      Teknik ozellikler, topluluk sinyalleri ve issue patternleri birlikte okunur.
                    </p>
                  </div>
                </div>

                <div className="mt-4 border-t border-slate-100 pt-4">
                  <IntelligenceScoreBreakdown
                    overallScore={scoreBreakdown.overallScore}
                    metrics={scoreBreakdown.metrics}
                    compact
                    summary={response.quick_verdict}
                  />
                </div>

                <div className="mt-4 border-t border-slate-100 pt-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="rounded-[1.25rem] border border-emerald-100 bg-emerald-50/60 p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-emerald-700">One cikan gucler</p>
                      <div className="mt-3 space-y-2">
                        {response.strengths.slice(0, 3).map((strength) => (
                          <div key={strength} className="flex items-start gap-2">
                            <span aria-hidden="true" className="mt-0.5 shrink-0 text-xs font-bold text-emerald-500">
                              +
                            </span>
                            <p className="text-xs leading-[1.65] text-slate-700">{strength}</p>
                          </div>
                        ))}
                        {response.strengths.length === 0 && (
                          <p className="text-xs text-slate-400">Belirgin guc sinyali cikmadi.</p>
                        )}
                      </div>
                    </div>

                    <div className="rounded-[1.25rem] border border-rose-100 bg-rose-50/60 p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-rose-700">Dikkat gerektiren noktalar</p>
                      <div className="mt-3 space-y-2">
                        {response.weaknesses.slice(0, 3).map((weakness) => (
                          <div key={weakness} className="flex items-start gap-2">
                            <span aria-hidden="true" className="mt-0.5 shrink-0 text-xs font-bold text-rose-500">
                              -
                            </span>
                            <p className="text-xs leading-[1.65] text-slate-700">{weakness}</p>
                          </div>
                        ))}
                        {response.weaknesses.length === 0 && (
                          <p className="text-xs text-slate-400">Belirgin zayiflik sinyali cikmadi.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {response.issue_warnings.length > 0 && (
                  <div className="mt-4 border-t border-slate-100 pt-4">
                    <p className="text-[11px] uppercase tracking-[0.16em] text-amber-700">Risk uyarilari</p>
                    <ul className="mt-3 space-y-2">
                      {response.issue_warnings.map((issue) => (
                        <li key={issue} className="rounded-[1.1rem] border border-amber-100 bg-amber-50/70 px-3 py-2.5">
                          <div className="flex items-start gap-2">
                            <span aria-hidden="true" className="mt-0.5 shrink-0 text-xs font-bold text-amber-500">
                              !
                            </span>
                            <p className="text-xs leading-[1.65] text-slate-700">{issue}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-5">
        <DataCredibilityCard />
      </div>
    </SectionCard>
  );
}
