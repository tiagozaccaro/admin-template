"use client"

import { useEffect, useState } from "react"

import { getApiUrl } from "@/lib/api"

type ApiUser = {
  id: string
  keycloak_sub: string
  email: string
  display_name: string | null
}

export default function AccountPage() {
  const [user, setUser] = useState<ApiUser | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`${getApiUrl()}/auth/me`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`)
        return (await res.json()) as ApiUser
      })
      .then((data) => {
        if (!cancelled) setUser(data)
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(
            err instanceof Error ? err.message : "Failed to load account"
          )
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="flex flex-col gap-4 px-4 py-4 md:gap-6 md:py-6 lg:px-6">
      <div>
        <h1 className="text-2xl font-semibold">Account</h1>
        <p className="text-muted-foreground">
          Your profile and account details.
        </p>
      </div>

      {error ? (
        <p className="text-destructive">{error}</p>
      ) : !user ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="flex flex-col gap-2 rounded-lg border p-4">
          <div className="flex items-center gap-2">
            <span className="font-medium">Display name:</span>
            <span>{user.display_name || "—"}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">Email:</span>
            <span>{user.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">User ID:</span>
            <span className="font-mono text-sm">{user.id}</span>
          </div>
        </div>
      )}
    </div>
  )
}
