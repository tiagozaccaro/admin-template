import { cookies } from "next/headers"
import { NextResponse } from "next/server"

import { getApiUrl } from "@/lib/api"

const SESSION_COOKIE = "admin_template_session"

async function revokeBackendSession(sessionId: string | undefined) {
  try {
    await fetch(`${getApiUrl()}/auth/logout`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(sessionId ? { Cookie: `${SESSION_COOKIE}=${sessionId}` } : {}),
      },
    })
  } catch {
    // Best effort: the browser session is cleared below even when the API
    // is unreachable, so the user can always get back to the login page.
  }
}

function clearSessionAndRedirect(request: Request) {
  const response = NextResponse.redirect(new URL("/login", request.url), 303)

  // The backend-issued session cookie is httpOnly, so only the server can
  // delete it. Clear the legacy client-side login marker as well.
  response.cookies.delete(SESSION_COOKIE)
  response.cookies.delete("isLoggedIn")

  return response
}

export async function POST(request: Request) {
  const cookieStore = await cookies()
  await revokeBackendSession(cookieStore.get(SESSION_COOKIE)?.value)
  return clearSessionAndRedirect(request)
}

export async function GET(request: Request) {
  const cookieStore = await cookies()
  await revokeBackendSession(cookieStore.get(SESSION_COOKIE)?.value)
  return clearSessionAndRedirect(request)
}
