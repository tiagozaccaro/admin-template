/**
 * Web OIDC callback route.
 *
 * Keycloak redirects here after the user authenticates. Exchanges the
 * authorization code for tokens (Authorization Code + PKCE, per
 * contracts/auth-oidc.md and T018), stores them in memory, then redirects
 * to the home page. On failure, redirects to the home page with an error
 * flag so the UI can surface a login error.
 *
 * No app-issued long-lived tokens are persisted (constitution VI).
 */

import { NextRequest, NextResponse } from "next/server"
import { handleCallback } from "@/src/lib/auth"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get("code")
  const state = searchParams.get("state")
  const error = searchParams.get("error")

  if (error) {
    return NextResponse.redirect(
      new URL("/?auth_error=access_denied", request.nextUrl.origin)
    )
  }

  if (!code || !state) {
    return NextResponse.redirect(
      new URL("/?auth_error=missing_params", request.nextUrl.origin)
    )
  }

  try {
    await handleCallback(code, state)
    return NextResponse.redirect(new URL("/", request.nextUrl.origin))
  } catch {
    return NextResponse.redirect(
      new URL("/?auth_error=token_exchange_failed", request.nextUrl.origin)
    )
  }
}
