import Link from "next/link";

import { Pill } from "@/components/pill";
import type { Product } from "@/types/product";

type ProductCardProps = {
  product: Product;
};

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      href={`/products/${product.slug}`}
      className="group relative block overflow-hidden rounded-[2rem] border border-slate-200/80 bg-white/95 p-5 shadow-soft transition duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-glow"
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-20 bg-[radial-gradient(circle_at_top,_rgba(15,23,42,0.05),_transparent_70%)] opacity-0 transition duration-300 group-hover:opacity-100" />

      <div className="relative">
        {/* Kimlik */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
              {product.family} · {product.release_year}
            </p>
            <h3 className="mt-2 text-xl font-semibold tracking-tight text-slate-950 sm:text-[1.35rem]">
              {product.name}
            </h3>
          </div>
          <Pill label={product.display_size} />
        </div>

        {/* Kisa aciklama */}
        <p className="mt-3 text-sm leading-6 text-slate-600">{product.short_description}</p>

        {/* Ozellik etiketleri */}
        <div className="mt-4 flex flex-wrap gap-2">
          {product.notable_highlights.slice(0, 3).map((highlight) => (
            <Pill key={highlight} label={highlight} />
          ))}
        </div>

        {/* Teknik ozet — 2 sutun mobilde, 3 sutun geniste */}
        <div className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-3">
          <article className="rounded-[1.25rem] border border-slate-200 bg-slate-50/80 p-3">
            <p className="text-[10px] uppercase tracking-[0.16em] text-slate-400">Chipset</p>
            <p className="mt-1.5 text-xs font-semibold leading-5 text-slate-900">{product.chipset}</p>
          </article>
          <article className="rounded-[1.25rem] border border-slate-200 bg-slate-50/80 p-3">
            <p className="text-[10px] uppercase tracking-[0.16em] text-slate-400">Pil</p>
            <p className="mt-1.5 text-xs font-semibold leading-5 text-slate-900">{product.battery_summary}</p>
          </article>
          <article className="col-span-2 rounded-[1.25rem] border border-slate-200 bg-slate-50/80 p-3 sm:col-span-1">
            <p className="text-[10px] uppercase tracking-[0.16em] text-slate-400">Kamera</p>
            <p className="mt-1.5 text-xs font-semibold leading-5 text-slate-900">{product.camera_summary}</p>
          </article>
        </div>

        {/* CTA alt satir */}
        <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
          <p className="text-sm text-slate-500">Tam urun zekasi gorunumu</p>
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-sm text-slate-700 transition group-hover:border-slate-900 group-hover:bg-slate-950 group-hover:text-white">
            →
          </span>
        </div>
      </div>
    </Link>
  );
}
