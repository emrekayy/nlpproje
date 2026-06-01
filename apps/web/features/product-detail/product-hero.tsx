import { Pill } from "@/components/pill";
import { getCommunitySentimentLabel } from "@/lib/utils";
import type { Product, ReviewSummary } from "@/types/product";

type ProductHeroProps = {
  product: Product;
  reviewSummary: ReviewSummary;
};

export function ProductHero({ product, reviewSummary }: ProductHeroProps) {
  const quickLookItems = [
    { label: "Cikis yili", value: String(product.release_year) },
    { label: "Chipset", value: product.chipset },
    { label: "Ekran", value: `${product.display_type} · ${product.display_size}` },
    { label: "Agirlik", value: product.weight },
  ];

  return (
    <section className="relative overflow-hidden rounded-[2.25rem] bg-slate-950 p-6 text-white shadow-glow sm:p-8 lg:p-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(148,163,184,0.22),_transparent_26%),radial-gradient(circle_at_top_right,_rgba(96,165,250,0.18),_transparent_28%)]" />

      <div className="relative grid gap-8 xl:grid-cols-[minmax(0,1.5fr),minmax(0,1fr)] xl:items-start">
        {/* Sol — kimlik + duygu */}
        <div>
          <span className="inline-block rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-slate-300">
            {product.family}
          </span>

          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl lg:text-5xl">
            {product.name}
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300 sm:text-[0.9375rem]">
            {product.short_description}
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Topluluk hissi</p>
              <p className="mt-2 text-base font-semibold tracking-tight text-white">
                {getCommunitySentimentLabel(reviewSummary)}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Pil</p>
              <p className="mt-2 text-sm font-medium leading-6 text-white">{product.battery_summary}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Kamera</p>
              <p className="mt-2 text-sm font-medium leading-6 text-white">{product.camera_summary}</p>
            </div>
          </div>

          <div className="mt-5 rounded-[1.75rem] border border-white/10 bg-white/[0.06] p-5">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Topluluk gorusu</p>
            <p className="mt-3 text-sm leading-7 text-slate-200">{reviewSummary.overall_sentiment_summary}</p>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {product.notable_highlights.map((highlight) => (
              <Pill key={highlight} label={highlight} tone="dark" />
            ))}
          </div>
        </div>

        {/* Sag — hizli bakis + gucler */}
        <div className="flex flex-col gap-4">
          <div className="rounded-[1.9rem] border border-white/10 bg-white/[0.07] p-5">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Hizli bakis</p>
            <dl className="mt-4 grid grid-cols-1 gap-3">
              {quickLookItems.map(({ label, value }) => (
                <div key={label} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-black/10 px-4 py-3">
                  <dt className="text-[11px] uppercase tracking-[0.16em] text-slate-400">{label}</dt>
                  <dd className="text-sm font-semibold text-white">{value}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="rounded-[1.9rem] border border-white/10 bg-white/[0.07] p-5">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">One cikan gucler</p>
            <ul className="mt-4 space-y-2.5">
              {reviewSummary.top_positive_aspects.slice(0, 3).map((aspect) => (
                <li key={aspect} className="flex items-start gap-2.5 text-sm">
                  <span className="mt-0.5 shrink-0 text-emerald-400" aria-hidden="true">+</span>
                  <span className="leading-6 text-slate-200">{aspect}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
