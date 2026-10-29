"use client"

import { AppSidebar } from "@workspace/ui/components/app-sidebar"
import { SiteHeader } from "@workspace/ui/components/site-header"
import { SidebarInset, SidebarProvider } from "@workspace/ui/components/sidebar"

type User = {
  name: string
  email: string
  avatar: string
}

export function DashboardLayoutClient({
  children,
  user,
}: {
  children: React.ReactNode
  user: User
}) {
  async function handleSignOut() {
    let sessionCleared = false

    try {
      // Same-origin route: it revokes the backend session and deletes the
      // httpOnly session cookie. A hard navigation below guarantees the
      // proxy sees the cleared cookie.
      await fetch("/auth/logout", { method: "POST" })
      sessionCleared = true
    } catch {
      // Fall back to the GET form of the same route.
    }

    try {
      localStorage.removeItem("isLoggedIn")
    } catch {}

    window.location.replace(sessionCleared ? "/login" : "/auth/logout")
  }

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" user={user} onSignOut={handleSignOut} />
      <SidebarInset>
        <SiteHeader />
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}
