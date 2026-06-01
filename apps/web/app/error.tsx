"use client";

import Link from "next/link";
import { useEffect } from "react";

type ErrorPageProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error("[App Error]", error);
  }, [error]);

  return (
    <main className="flex min-h-[60vh] items-center justify-center">
      <div className="max-w-md rounded-3xl border border-slate-200 bg-white/90 p-8 text-center shadow-soft">
        <p className="text-sm uppercase tracking-[0.32em] text-slate-400">Hata</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">Bir sorun olustu</h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          Veriler yuklenirken bir hata olustu. Backend servisinin calisir durumda oldugunu dogrulayin.
        </p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            type="button"
            onClick={reset}
            className="inline-flex justify-center rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
          >
            Tekrar dene
          </button>
          <Link
            href="/"
            className="inline-flex justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Ana sayfaya don
          </Link>
        </div>
      </div>
    </main>
  );
}
