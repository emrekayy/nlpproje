import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#0f172a",
        card: "#111827",
        accent: "#60a5fa"
      },
      boxShadow: {
        soft: "0 20px 50px rgba(15, 23, 42, 0.10)",
        panel: "0 18px 44px rgba(15, 23, 42, 0.12)",
        glow: "0 24px 70px rgba(15, 23, 42, 0.16)"
      }
    }
  },
  plugins: []
};

export default config;
