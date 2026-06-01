import { ProductSearchExperience } from "@/features/search/product-search-experience";
import { getProducts } from "@/services/product-service";

const FEATURES = [
  {
    index: "01",
    title: "User Review Analysis",
    description: "Topluluk geri bildirimlerini guclu yanlar, zayif sinyaller ve tekrar eden memnuniyet temalari halinde ozetler.",
  },
  {
    index: "02",
    title: "Technical Specs Intelligence",
    description: "Chipset, ekran, kamera ve pil sinyallerini sadece teknik liste olarak degil karar verdiren baglamla sunar.",
  },
  {
    index: "03",
    title: "Risk Signal Detection",
    description: "Kronik sorun basliklari ve tekrar eden issue patternleri daha erken fark edilsin diye ayristirilir.",
  },
  {
    index: "04",
    title: "AI Recommendations",
    description: "Hazir sorular ve serbest metin uzerinden satin alma kararini netlestiren grounded oneriler uretir.",
  },
] as const;

export default async function HomePage() {
  const { items } = await getProducts();
  const years = items.map((item) => item.release_year);
  const latestYear = years.length > 0 ? Math.max(...years) : 2026;
  const earliestYear = years.length > 0 ? Math.min(...years) : 2020;
  const chipsetCount = new Set(items.map((item) => item.chipset)).size;

  return (
    <main className="space-y-8 lg:space-y-10">
      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-[2.25rem] bg-slate-950 px-6 py-8 text-white shadow-glow sm:px-8 md:px-10 md:py-12">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(148,163,184,0.2),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(96,165,250,0.18),_transparent_28%)]" />

        <div className="relative grid gap-8 xl:grid-cols-[minmax(0,1.5fr),minmax(0,1fr)] xl:items-start">
          {/* Sol */}
          <div>
            <span className="inline-flex items-center rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.28em] text-slate-300">
              AI Product Intelligence
            </span>

            <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-[1.15] tracking-tight text-white sm:text-5xl lg:text-6xl">
              iPhone modellerini spesifikasyon, topluluk sinyali ve AI analiziyle kesfet.
            </h1>

            <p className="mt-5 max-w-xl text-[0.9375rem] leading-7 text-slate-300">
              Teknik ozellikler, kullanici gorusleri ve kronik sorun basliklarini tek bir premium panelde gorun.
            </p>

            {/* Istatistik cubuklar */}
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {[
                { label: "Model", value: String(items.length), detail: "katalogda" },
                { label: "Nesil", value: `${earliestYear}–${latestYear}`, detail: "kapsam araligi" },
                { label: "Chipset", value: `${chipsetCount}`, detail: "farkli platform" },
              ].map(({ label, value, detail }) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/10 p-4">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{label}</p>
                  <p className="mt-2 text-2xl font-semibold tracking-tight text-white">{value}</p>
                  <p className="mt-1 text-sm text-slate-400">{detail}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Sag — platform aciklamasi */}
          <div className="rounded-[2rem] border border-white/10 bg-white/[0.07] p-5">
            <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Platform ne saglar?</p>
            <div className="mt-5 space-y-3">
              {[
                {
                  title: "Hizli urun hakimiyeti",
                  description: "Teknik sinyalleri ve topluluk gorusunu modeli incelemeden once tek bakista gorun.",
                },
                {
                  title: "Karar odakli hiyerarsi",
                  description: "Guclu yanlar, risk basliklari ve kullanim profilleri net bir duzende sunulur.",
                },
                {
                  title: "Grounded AI yardimi",
                  description: "Sohbet paneli mevcut veri katmanina dayali, daha guvenilir yanitlar uretir.",
                },
              ].map((item) => (
                <div key={item.title} className="rounded-2xl border border-white/10 bg-black/10 p-4">
                  <p className="text-sm font-semibold text-white">{item.title}</p>
                  <p className="mt-1.5 text-sm leading-6 text-slate-300">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Ozellik tanitim kartlari ─────────────────────── */}
      <section className="space-y-4">
        <div className="max-w-2xl">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Intelligence layers</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
            Satin alma kararini destekleyen dort ana zeka katmani.
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Mevcut katalog deneyimini bozmadan, her adimda daha guvenilir ve daha urun-odakli bir okuma sunar.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {FEATURES.map((feat) => (
          <article
            key={feat.index}
            className="group relative overflow-hidden rounded-[1.9rem] border border-slate-200/70 bg-white/90 p-5 shadow-soft transition duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_24px_60px_-34px_rgba(15,23,42,0.28)]"
          >
            <div className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-[radial-gradient(circle_at_top,_rgba(15,23,42,0.08),_transparent_72%)] opacity-0 transition duration-300 group-hover:opacity-100" />
            <div className="relative">
              <div className="flex items-center justify-between gap-3">
                <span className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-400">{feat.index}</span>
                <span className="h-2.5 w-2.5 rounded-full bg-slate-300 transition duration-300 group-hover:bg-slate-900" />
              </div>
              <p className="mt-4 text-base font-semibold tracking-tight text-slate-950">{feat.title}</p>
              <p className="mt-2 text-sm leading-6 text-slate-500">{feat.description}</p>
            </div>
          </article>
        ))}
        </div>
      </section>

      {/* ── Arama + urun listesi ─────────────────────────── */}
      <ProductSearchExperience products={items} />
    </main>
  );
}
