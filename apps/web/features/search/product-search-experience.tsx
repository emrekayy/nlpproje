"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { ProductCard } from "@/features/search/product-card";
import { SearchInput } from "@/features/search/search-input";
import type { Product } from "@/types/product";

type ProductSearchExperienceProps = {
  products: Product[];
};

export function ProductSearchExperience({ products }: ProductSearchExperienceProps) {
  const [query, setQuery] = useState("");

  const filteredProducts = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return products;

    return products.filter((product) => {
      const searchIndex = [
        product.name,
        product.family,
        product.chipset,
        product.release_year.toString(),
        ...product.notable_highlights,
      ]
        .join(" ")
        .toLowerCase();

      return searchIndex.includes(normalized);
    });
  }, [products, query]);

  const suggestions = filteredProducts.slice(0, 5);

  return (
    <section className="space-y-6">
      <div className="rounded-[1.9rem] border border-slate-200/70 bg-white/70 p-5 shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.22)] sm:p-6">
        <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">Model katalogu</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
          Dogru modeli bulmak icin arayin ve karsilastirin.
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Model adi, yil, chipset veya one cikan ozellige gore anlik filtreleme yapabilirsiniz.
        </p>
      </div>

      <SearchInput value={query} onChange={setQuery} resultCount={filteredProducts.length} />

      {!!query && suggestions.length > 0 && (
        <div className="rounded-[1.75rem] border border-slate-200/70 bg-white/90 p-4 shadow-soft transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_50px_-30px_rgba(15,23,42,0.22)]">
          <p className="text-sm font-medium text-slate-800">Hizli erisim</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {suggestions.map((product) => (
              <Link
                key={product.slug}
                href={`/products/${product.slug}`}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 transition duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white"
              >
                {product.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {filteredProducts.length > 0 ? (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {filteredProducts.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      ) : (
        <div className="rounded-[2rem] border border-dashed border-slate-300 bg-white/70 px-6 py-10 text-center shadow-soft">
          <p className="text-lg font-semibold tracking-tight text-slate-900">Eslesen model bulunamadi</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Daha genel bir terim, yil veya chipset ile aramayi genisletebilirsiniz.
          </p>
        </div>
      )}
    </section>
  );
}
