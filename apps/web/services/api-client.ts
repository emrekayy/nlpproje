const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const { headers: initHeaders, ...restInit } = init ?? {};

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...restInit,
    headers: {
      "Content-Type": "application/json",
      ...(initHeaders instanceof Headers
        ? Object.fromEntries(initHeaders.entries())
        : (initHeaders as Record<string, string> | undefined) ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`[${response.status}] ${path}: ${detail}`);
  }

  return response.json() as Promise<T>;
}
