"use client"

/**
 * Client-side session cookie helpers for the web app.
 *
 * The backend issues the session as an httpOnly cookie
 * (``admin_template_session`` by default), so the web client only needs to
 * clear it on logout.
 */

export const sessionCookieName = "admin_template_session"

export function clearSessionCookie() {
  document.cookie = `${sessionCookieName}=; Path=/; Max-Age=0`
}
