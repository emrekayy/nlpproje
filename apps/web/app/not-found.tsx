import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-[60vh] items-center justify-center">
      <div className="max-w-md rounded-3xl border border-slate-200 bg-white/90 p-8 text-center shadow-soft">
        <p className="text-sm uppercase tracking-[0.32em] text-slate-400">404</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">Urun bulunamadi</h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          Istenen iPhone kaydi bulunamadi veya backend servisi su anda erisilebilir degil.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          Ana sayfaya don
        </Link>
      </div>
    </main>
  );
}
