import { cn, getScoreColor, type IntelligenceScoreMetric } from "@/lib/utils";

type IntelligenceScoreBreakdownProps = {
  overallScore: number;
  metrics: IntelligenceScoreMetric[];
  compact?: boolean;
  summary?: string;
};

export function IntelligenceScoreBreakdown({
  overallScore,
  metrics,
  compact = false,
  summary,
}: IntelligenceScoreBreakdownProps) {
  const overallColor = getScoreColor(overallScore);

  return (
    <div
      className={cn(
        "grid gap-3",
        compact ? "lg:grid-cols-1" : "lg:grid-cols-[minmax(0,0.95fr),minmax(0,1.25fr)]"
      )}
    >
      <div className="rounded-[1.5rem] border border-slate-200 bg-slate-950 p-5 text-white shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-glow">
        <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Overall Score</p>
        <div className="mt-4 flex items-end gap-2">
          <p className="text-4xl font-semibold tracking-tight text-white sm:text-[2.75rem]">
            {overallScore}
          </p>
          <p className="pb-1 text-sm text-slate-400">/100</p>
        </div>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className={cn("h-full rounded-full transition-all duration-700", overallColor.bar)}
            style={{ width: `${overallScore}%` }}
          />
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          {summary ??
            "Donanim dengesi, topluluk memnuniyeti ve risk sinyalleri birlikte okunarak olusturulan genel sinyal."}
        </p>
      </div>

      <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50/80 p-4 shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_18px_45px_-28px_rgba(15,23,42,0.35)] sm:p-5">
        <div className="space-y-3">
          {metrics.map((metric) => {
            const color = getScoreColor(metric.score);

            return (
              <div key={metric.label}>
                <div className="mb-1.5 flex items-center justify-between gap-3">
                  <p
                    className={cn(
                      "text-slate-600",
                      compact ? "text-xs font-medium" : "text-sm font-medium"
                    )}
                  >
                    {metric.label}
                  </p>
                  <p className={cn("font-semibold tabular-nums", color.text, compact ? "text-xs" : "text-sm")}>
                    {metric.score}
                  </p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white">
                  <div
                    className={cn("h-full rounded-full transition-all duration-700", color.bar)}
                    style={{ width: `${metric.score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
