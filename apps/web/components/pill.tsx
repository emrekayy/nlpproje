import { cn } from "@/lib/utils";

type PillProps = {
  label: string;
  tone?: "neutral" | "positive" | "negative" | "warning" | "dark";
};

export function Pill({ label, tone = "neutral" }: PillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1.5 text-[11px] font-medium tracking-[0.02em]",
        tone === "positive" && "border-emerald-200 bg-emerald-50 text-emerald-700",
        tone === "negative" && "border-rose-200 bg-rose-50 text-rose-700",
        tone === "warning" && "border-amber-200 bg-amber-50 text-amber-700",
        tone === "dark" && "border-white/15 bg-white/10 text-white",
        tone === "neutral" && "border-slate-200 bg-slate-50 text-slate-700"
      )}
    >
      {label}
    </span>
  );
}
