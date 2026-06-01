import { Pill } from "@/components/pill";
import { SectionCard } from "@/components/section-card";
import type { ReviewSummary } from "@/types/product";

type ReviewSummaryCardProps = {
  summary: ReviewSummary;
};

export function ReviewSummaryCard({ summary }: ReviewSummaryCardProps) {
  return (
    <SectionCard
      title="Topluluk Gorusu"
      description="Gercek kullanici geri bildirimlerinden cikarilan guclu ve zayif sinyaller."
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[1.75rem] border border-emerald-100 bg-emerald-50/60 p-5">
          <p className="text-[11px] uppercase tracking-[0.2em] text-emerald-700">Guclu yonler</p>
          {summary.top_positive_aspects.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {summary.top_positive_aspects.map((aspect) => (
                <Pill key={aspect} label={aspect} tone="positive" />
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-400">Henuz veri yok.</p>
          )}
        </div>

        <div className="rounded-[1.75rem] border border-rose-100 bg-rose-50/60 p-5">
          <p className="text-[11px] uppercase tracking-[0.2em] text-rose-700">Zayif yonler</p>
          {summary.top_negative_aspects.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {summary.top_negative_aspects.map((aspect) => (
                <Pill key={aspect} label={aspect} tone="negative" />
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-400">Henuz veri yok.</p>
          )}
        </div>
      </div>
    </SectionCard>
  );
}
