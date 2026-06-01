type SearchInputProps = {
  value: string;
  onChange: (value: string) => void;
  resultCount: number;
};

export function SearchInput({ value, onChange, resultCount }: SearchInputProps) {
  return (
    <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 p-4 shadow-soft sm:p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        {/* Arama alani */}
        <div className="min-w-0 flex-1">
          <label className="mb-2 block text-sm font-medium text-slate-800" htmlFor="product-search">
            Model ara
          </label>
          <div className="flex items-center gap-3 rounded-[1.35rem] border border-slate-200 bg-slate-50 px-4 py-3 transition focus-within:border-slate-300 focus-within:bg-white">
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              className="h-4.5 w-4.5 shrink-0 text-slate-400"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              width="18"
              height="18"
            >
              <circle cx="11" cy="11" r="6" />
              <path d="m20 20-4.2-4.2" />
            </svg>
            <input
              id="product-search"
              value={value}
              onChange={(event) => onChange(event.target.value)}
              placeholder="Orn. iPhone 15 Pro Max"
              className="w-full border-0 bg-transparent p-0 text-[15px] text-slate-900 outline-none placeholder:text-slate-400"
            />
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Model adi, yil, chipset veya one cikan ozelliklere gore arayabilirsiniz.
          </p>
        </div>

        {/* Sonuc sayaci */}
        <div className="shrink-0 rounded-[1.35rem] border border-slate-200 bg-slate-50 px-5 py-3 sm:min-w-[9rem] sm:text-center">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Sonuc</p>
          <p className="mt-1.5 text-2xl font-semibold tracking-tight text-slate-950">{resultCount}</p>
          <p className="mt-0.5 text-xs text-slate-500">model gorunuyor</p>
        </div>
      </div>
    </div>
  );
}
