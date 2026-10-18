/**
 * API base URL for the Admin Template FastAPI backend.
 *
 * Defaults to http://localhost:8000 (the API port). Override with the
 * NEXT_PUBLIC_API_URL environment variable in production.
 */

export const API_BASE_URL =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) ||
  "http://localhost:8000"

/** Fetch JSON from the API, throwing on non-ok responses. */
export async function apiFetch<T = unknown>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: init?.headers ? { "Content-Type": "application/json", ...init.headers } : { "Content-Type": "application/json" },
    ...init,
  })
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }
  return (await response.json()) as T
}
