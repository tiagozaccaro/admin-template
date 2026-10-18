"use client"

/**
 * Google OAuth client helpers for the Next.js web app.
 *
 * Initiates the Authorization Code flow against the backend's
 * /auth/google/start endpoint and redirects the user agent to Google.
 * The backend issues an httpOnly session cookie on the callback, so the
 * web client never handles tokens directly.
 */

export function getApiUrl(): string {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  return "http://localhost:8000"
}

export async function startGoogleSignIn(): Promise<void> {
  const response = await fetch(`${getApiUrl()}/auth/google/start`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  })
  if (!response.ok) {
    throw new Error("Failed to start Google sign-in")
  }
  const body = (await response.json()) as { authorization_url: string }
  window.location.href = body.authorization_url
}
