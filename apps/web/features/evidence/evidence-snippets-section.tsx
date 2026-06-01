import { SectionCard } from "@/components/section-card";
import type { EvidenceSnippet } from "@/types/product";

type EvidenceSnippetsSectionProps = {
  evidence: EvidenceSnippet[];
};

export function EvidenceSnippetsSection({ evidence }: EvidenceSnippetsSectionProps) {
  return (
    <SectionCard
      title="Kullanici Kaniti"
      description="Gercek kullanici geri bildirimlerinden derlenen somut alintilar ve kaynak bilgileri."
    >
      {evidence.length > 0 ? (
        <div className="grid gap-3 lg:grid-cols-2">
          {evidence.map((snippet, index) => (
            <blockquote
              key={`${snippet.source}-${index}`}
              className="rounded-[1.75rem] border border-slate-200 bg-slate-50/80 p-5"
            >
              <p className="text-sm leading-7 text-slate-700">&ldquo;{snippet.text}&rdquo;</p>
              <footer className="mt-4 flex items-center gap-2 border-t border-slate-200 pt-3">
                <span className="h-px w-4 shrink-0 bg-slate-300" aria-hidden="true" />
                <span className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{snippet.source}</span>
              </footer>
            </blockquote>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">Henuz kullanici kaniti bulunamadi.</p>
      )}
    </SectionCard>
  );
}
