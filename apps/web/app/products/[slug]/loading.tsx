export default function ProductDetailLoading() {
  return (
    <div className="space-y-8">
      {/* Back link skeleton */}
      <div className="h-4 w-36 animate-pulse rounded-full bg-slate-200" />

      {/* Hero skeleton */}
      <div className="animate-pulse rounded-3xl bg-slate-900/80 p-8 sm:p-10">
        <div className="grid gap-8 lg:grid-cols-[1.7fr,1fr]">
          <div className="space-y-4">
            <div className="h-3 w-24 rounded-full bg-slate-700" />
            <div className="h-10 w-72 rounded-2xl bg-slate-700" />
            <div className="h-4 w-full rounded-lg bg-slate-700/60" />
            <div className="h-4 w-4/5 rounded-lg bg-slate-700/60" />
            <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="h-3 w-32 rounded-full bg-slate-700" />
              <div className="mt-2 h-4 w-full rounded-lg bg-slate-700/50" />
              <div className="mt-1 h-4 w-3/4 rounded-lg bg-slate-700/50" />
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i}>
                  <div className="h-2 w-16 rounded-full bg-slate-700" />
                  <div className="mt-1.5 h-4 w-28 rounded-lg bg-slate-600" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main grid skeleton */}
      <div className="grid gap-8 xl:grid-cols-[minmax(0,2fr),380px]">
        <div className="space-y-6">
          {/* Quick verdict skeleton */}
          <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
            <div className="h-5 w-36 rounded-xl bg-slate-200" />
            <div className="mt-1 h-4 w-72 rounded-lg bg-slate-100" />
            <div className="mt-5 h-24 rounded-2xl bg-slate-100" />
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div className="h-32 rounded-2xl bg-emerald-50" />
              <div className="h-32 rounded-2xl bg-amber-50" />
            </div>
          </div>

          {/* Specs skeleton */}
          <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
            <div className="h-5 w-44 rounded-xl bg-slate-200" />
            <div className="mt-1 h-4 w-64 rounded-lg bg-slate-100" />
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {Array.from({ length: 6 }).map((_, j) => (
                <div key={j} className="rounded-2xl bg-slate-100 p-5">
                  <div className="h-2 w-20 rounded-full bg-slate-200" />
                  <div className="mt-2 h-4 w-full rounded-lg bg-slate-200" />
                  <div className="mt-2 h-3 w-3/4 rounded bg-slate-200/70" />
                </div>
              ))}
            </div>
          </div>

          {/* Review summary skeleton */}
          <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
            <div className="h-5 w-52 rounded-xl bg-slate-200" />
            <div className="mt-4 h-20 rounded-2xl bg-slate-100" />
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div className="h-28 rounded-2xl bg-emerald-50" />
              <div className="h-28 rounded-2xl bg-rose-50" />
            </div>
          </div>

          {/* Issues skeleton */}
          <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
            <div className="h-5 w-56 rounded-xl bg-slate-200" />
            <div className="mt-4 space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-2xl bg-slate-100 p-4">
                  <div className="flex justify-between gap-3">
                    <div className="h-4 w-1/2 rounded-lg bg-slate-200" />
                    <div className="h-5 w-20 rounded-full bg-amber-100" />
                  </div>
                  <div className="mt-3 h-3 w-full rounded bg-slate-200/70" />
                  <div className="mt-1 h-3 w-4/5 rounded bg-slate-200/70" />
                </div>
              ))}
            </div>
          </div>

          {/* Evidence skeleton */}
          <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
            <div className="h-5 w-40 rounded-xl bg-slate-200" />
            <div className="mt-4 space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-2xl bg-slate-100 p-5">
                  <div className="h-3 w-full rounded bg-slate-200/70" />
                  <div className="mt-2 h-3 w-5/6 rounded bg-slate-200/70" />
                  <div className="mt-3 h-2 w-24 rounded-full bg-slate-200" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chatbot skeleton */}
        <div className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-6">
          <div className="h-5 w-28 rounded-xl bg-slate-200" />
          <div className="mt-1 h-4 w-48 rounded-lg bg-slate-100" />
          <div className="mt-4 h-20 rounded-2xl bg-slate-100" />
          <div className="mt-5 flex flex-wrap gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-7 w-28 rounded-full bg-slate-100" />
            ))}
          </div>
          <div className="mt-5 h-24 rounded-2xl bg-slate-100" />
          <div className="mt-3 h-11 rounded-2xl bg-slate-200" />
        </div>
      </div>
    </div>
  );
}
