import { SectionCard } from "@/components/section-card";
import type { Product } from "@/types/product";

type SpecsGridProps = {
  product: Product;
};

const buildSpecs = (product: Product) => [
  { label: "Chipset", value: product.chipset },
  { label: "Display", value: `${product.display_type} / ${product.display_size}` },
  { label: "Battery", value: product.battery_summary },
  { label: "Camera", value: product.camera_summary },
  { label: "Storage", value: product.storage_options.join(", ") },
  { label: "Weight", value: product.weight }
];

export function SpecsGrid({ product }: SpecsGridProps) {
  return (
    <SectionCard title="Teknik Ozellikler" description="Temel donanim ozeti ve satin alma oncesi hizli karsilastirma verileri.">
      <div className="grid gap-4 md:grid-cols-2">
        {buildSpecs(product).map((item) => (
          <div key={item.label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-2 text-sm font-medium leading-6 text-slate-900">{item.value}</p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}
