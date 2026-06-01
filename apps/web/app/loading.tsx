export default function Loading() {
  return (
    <div className="space-y-10">
      <div className="animate-pulse rounded-[2rem] border border-white/60 bg-white/60 p-8 md:p-12">
        <div className="h-3 w-48 rounded-full bg-slate-200" />
        <div className="mt-5 h-10 w-3/4 rounded-2xl bg-slate-200" />
        <div className="mt-4 h-5 w-1/2 rounded-xl bg-slate-200" />
      </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse rounded-3xl border border-slate-200 bg-white/90 p-5"
          >
            <div className="h-3 w-16 rounded-full bg-slate-200" />
            <div className="mt-2 h-6 w-40 rounded-xl bg-slate-200" />
            <div className="mt-4 h-4 w-full rounded-lg bg-slate-100" />
            <div className="mt-1 h-4 w-5/6 rounded-lg bg-slate-100" />
            <div className="mt-4 flex gap-2">
              <div className="h-6 w-20 rounded-full bg-slate-100" />
              <div className="h-6 w-24 rounded-full bg-slate-100" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
