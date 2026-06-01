import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SectionCardProps = {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
};

export function SectionCard({ title, description, children, className }: SectionCardProps) {
  return (
    <section
      className={cn(
        "rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-soft backdrop-blur-sm sm:p-7",
        className
      )}
    >
      {(title || description) && (
        <header className="mb-6">
          {title && <h2 className="text-lg font-semibold tracking-tight text-slate-950 sm:text-[1.35rem]">{title}</h2>}
          {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">{description}</p>}
        </header>
      )}
      {children}
    </section>
  );
}
