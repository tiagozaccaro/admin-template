import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { DashboardLayoutClient } from "./dashboard-layout-client"
import { getApiUrl } from "@/lib/api"

type ApiUser = {
  id: string
  keycloak_sub: string
  email: string
  display_name: string | null
}

async function getCurrentUser(): Promise<ApiUser | null> {
  const cookieStore = await cookies()
  const session = cookieStore.get("admin_template_session")

  let res: Response
  try {
    res = await fetch(`${getApiUrl()}/auth/me`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(session ? { Cookie: `${session.name}=${session.value}` } : {}),
      },
    })
  } catch {
    return null
  }

  if (!res.ok) {
    return null
  }

  return (await res.json()) as ApiUser
}

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const apiUser = await getCurrentUser()

  if (!apiUser) {
    // The proxy only checks that a session cookie exists. If the API rejects
    // it (expired/revoked or unavailable), clear it instead of rendering the
    // dashboard with a placeholder identity.
    redirect("/auth/logout")
  }

  const user = {
    name: apiUser.display_name || apiUser.email,
    email: apiUser.email,
    avatar: "/placeholder.svg",
  }

  return <DashboardLayoutClient user={user}>{children}</DashboardLayoutClient>
}
