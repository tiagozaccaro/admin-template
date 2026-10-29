import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { Geist, Geist_Mono, Inter } from "next/font/google"

import "@workspace/ui/globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@workspace/ui/lib/utils"
import { TooltipProvider } from "@workspace/ui/components/tooltip"
import { DashboardLayoutClient } from "@/components/dashboard-layout-client"
import { getApiUrl } from "@/lib/api"

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

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

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const apiUser = await getCurrentUser()

  // Allow auth pages to render without a session.
  // (Best-effort: redirect only when a session is expected.)

  const content = apiUser
    ? (() => {
        const user = {
          name: apiUser.display_name || apiUser.email,
          email: apiUser.email,
          avatar: "/placeholder.svg",
        }
        return (
          <DashboardLayoutClient user={user}>{children}</DashboardLayoutClient>
        )
      })()
    : children

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        "antialiased",
        fontMono.variable,
        "font-sans",
        inter.variable
      )}
    >
      <body>
        <ThemeProvider>
          <TooltipProvider>{content}</TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
