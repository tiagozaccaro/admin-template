import { cookies } from "next/headers"
import { redirect } from "next/navigation"

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

export default async function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const apiUser = await getCurrentUser()

  if (!apiUser) {
    redirect("/auth/logout")
  }

  return <>{children}</>
}
