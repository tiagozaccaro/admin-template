import { redirect } from "next/navigation"

/**
 * Google OIDC callback page.
 *
 * The backend validates the callback, issues the httpOnly session cookie,
 * and redirects here. Rendering is a no-op; we redirect to the dashboard so
 * the middleware can validate the session cookie.
 */

export default function CallbackPage({
  searchParams,
}: Readonly<{
  searchParams: { session_id?: string }
}>) {
  // The session cookie is already set by the backend response. Mobile
  // clients can read the session_id query parameter for secure storage.
  void searchParams
  redirect("/dashboard")
}
