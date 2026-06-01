import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";

export const metadata: Metadata = {
  title: "AI Product Intelligence Assistant",
  description: "Apple iPhone product intelligence app with specs, issue analysis and grounded chat."
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="tr">
      <body>
        <div className="mx-auto min-h-screen max-w-[92rem] px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10">
          {children}
        </div>
      </body>
    </html>
  );
}
