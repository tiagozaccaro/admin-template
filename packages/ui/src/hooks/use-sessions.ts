import * as React from "react"

export type Session = { id: string; title: string }

export function useSessions(initial: Session[] = []) {
  const [sessions, setSessions] = React.useState<Session[]>(initial)
  const [active, setActive] = React.useState<string | null>(
    initial[0]?.id ?? null
  )

  const create = React.useCallback((title = "New chat") => {
    const s: Session = { id: crypto.randomUUID(), title }
    setSessions((prev) => [...prev, s])
    setActive(s.id)
    return s
  }, [])

  const remove = React.useCallback((id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id))
    setActive((cur) => (cur === id ? null : cur))
  }, [])

  return { sessions, active, setActive, create, remove }
}
