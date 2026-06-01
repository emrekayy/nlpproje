import { SectionCard } from "@/components/section-card";
import { formatConfidenceScore } from "@/lib/utils";
import type { IssueItem } from "@/types/product";

type IssuesSectionProps = {
  issues: IssueItem[];
};

export function IssuesSection({ issues }: IssuesSectionProps) {
  return (
    <SectionCard
      title="Risk Sinyalleri"
      description="Topluluk geri bildirimlerinden derlenen, tekrar eden sorun basliklari ve guven skorlari."
    >
      {issues.length > 0 ? (
        <div className="grid gap-3">
          {issues.map((issue) => (
            <article key={issue.title} className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-start justify-between gap-4">
                <h3 className="min-w-0 text-[0.9375rem] font-semibold leading-snug tracking-tight text-slate-950">
                  {issue.title}
                </h3>
                <span className="shrink-0 whitespace-nowrap rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
                  {formatConfidenceScore(issue.confidence_score)}
                </span>
              </div>
              <p className="mt-3 text-sm leading-7 text-slate-600">{issue.description}</p>
            </article>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">Kayitli sorun basligi bulunamadi.</p>
      )}
    </SectionCard>
  );
}
