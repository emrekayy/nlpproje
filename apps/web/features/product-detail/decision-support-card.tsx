import { Pill } from "@/components/pill";
import { SectionCard } from "@/components/section-card";
import { formatRecommendationVerdict, getRecommendationTone } from "@/lib/utils";
import type { ProductDecisionSupport } from "@/types/product";

type DecisionSupportCardProps = {
  decisionSupport: ProductDecisionSupport;
};

function BulletList({ items, color }: { items: string[]; color: "emerald" | "amber" }) {
  const dotClass = color === "emerald" ? "bg-emerald-400" : "bg-amber-400";
  return (
    <ul className="mt-4 space-y-2.5">
      {items.map((item) => (
        <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700">
          <span className={`mt-[0.45rem] h-1.5 w-1.5 shrink-0 rounded-full ${dotClass}`} aria-hidden="true" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function DecisionSupportCard({ decisionSupport }: DecisionSupportCardProps) {
  return (
    <SectionCard
      title="Satin Alma Karar Destegi"
      description="Hangi kullanici icin ideal, hangi senaryo icin riskli — net bir ozet."
    >
      <div className="mt-4 rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5 transition duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-soft">
        <div className="flex flex-wrap items-center gap-3">
          <Pill
            label={formatRecommendationVerdict(decisionSupport.recommendation_verdict)}
            tone={getRecommendationTone(decisionSupport.recommendation_verdict)}
          />
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">2026 degerlendirmesi</p>
        </div>
        <p className="mt-4 text-sm leading-7 text-slate-700">{decisionSupport.quick_verdict}</p>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded-[1.75rem] border border-emerald-100 bg-emerald-50/50 p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
          <p className="text-[11px] uppercase tracking-[0.2em] text-emerald-700">Kime uygun</p>
          <BulletList items={decisionSupport.best_for} color="emerald" />
        </div>

        <div className="rounded-[1.75rem] border border-amber-100 bg-amber-50/50 p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-soft">
          <p className="text-[11px] uppercase tracking-[0.2em] text-amber-700">Kime riskli</p>
          <BulletList items={decisionSupport.not_ideal_for} color="amber" />
        </div>
      </div>
    </SectionCard>
  );
}
