import { Pill } from "@/components/pill";
import { SectionCard } from "@/components/section-card";
import type { Product } from "@/types/product";

type ProductOverviewProps = {
  product: Product;
};

function buildOverviewItems(product: Product) {
  return [
    {
      label: "Cikis yili",
      value: String(product.release_year),
      detail: `${product.release_year} nesli — yazilim destek omrunu belirler.`,
    },
    {
      label: "Chipset",
      value: product.chipset,
      detail: "Gunluk akicilik, oyun ve uzun vadeli verimlilik.",
    },
    {
      label: "Ekran",
      value: `${product.display_type} · ${product.display_size}`,
      detail: "Panel teknolojisi ve boyut medya deneyimini dogrudan etkiler.",
    },
    {
      label: "Pil",
      value: product.battery_summary,
      detail: "Topluluktan derlenen uzun donem dayaniklilik izlenimi.",
    },
    {
      label: "Kamera",
      value: product.camera_summary,
      detail: "Foto ve video performansi icin hizli karar aldiran ozet.",
    },
    {
      label: "Agirlik",
      value: product.weight,
      detail: "Elde hissedilen konfor ve tasima deneyimine dogrudan etkisi var.",
    },
  ];
}

export function ProductOverview({ product }: ProductOverviewProps) {
  return (
    <SectionCard
      title="Teknik Ozellikler"
      description="Satin alma oncesi hizli referans icin temel donanim sinyalleri."
    >
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {buildOverviewItems(product).map((item) => (
          <article key={item.label} className="rounded-[1.5rem] border border-slate-200 bg-slate-50/80 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{item.label}</p>
            <p className="mt-2.5 text-sm font-semibold leading-6 text-slate-950">{item.value}</p>
            <p className="mt-1.5 text-xs leading-5 text-slate-500">{item.detail}</p>
          </article>
        ))}
      </div>

      <div className="mt-4 flex flex-col gap-3 rounded-[1.75rem] border border-slate-200 bg-white p-5 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Depolama secenekleri</p>
        <div className="flex flex-wrap gap-2">
          {product.storage_options.map((option) => (
            <Pill key={option} label={option} />
          ))}
        </div>
      </div>
    </SectionCard>
  );
}
