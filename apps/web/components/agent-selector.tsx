"use client"

import * as React from "react"
import { Check, ChevronsDown, CircleX, Plug, Server } from "lucide-react"

import { cn } from "@workspace/ui/lib/utils"

export type AgentOption = {
  id: string
  name: string
  url: string
  status: "healthy" | "unhealthy" | "offline" | "pending"
}

type AgentSelectorProps = {
  agents: AgentOption[]
  value?: string | null
  onChange: (agent: AgentOption | null) => void
  disabled?: boolean
  placeholder?: string
}

function statusIcon(status: AgentOption["status"]) {
  switch (status) {
    case "healthy":
      return <Check className="h-4 w-4 text-emerald-500" />
    case "unhealthy":
      return <CircleX className="h-4 w-4 text-amber-500" />
    case "offline":
      return <CircleX className="h-4 w-4 text-muted-foreground" />
    default:
      return <Server className="h-4 w-4 text-muted-foreground" />
  }
}

export function AgentSelector({
  agents,
  value,
  onChange,
  disabled,
  placeholder = "Select agent...",
}: AgentSelectorProps) {
  const [open, setOpen] = React.useState(false)
  const [query, setQuery] = React.useState("")
  const wrapperRef = React.useRef<HTMLDivElement>(null)

  const selected = React.useMemo(
    () => agents.find((a) => a.id === value) ?? null,
    [agents, value]
  )

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return agents
    return agents.filter(
      (a) => a.name.toLowerCase().includes(q) || a.url.toLowerCase().includes(q)
    )
  }, [agents, query])

  React.useEffect(() => {
    function onClickOutside(event: MouseEvent) {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", onClickOutside)
    return () => document.removeEventListener("mousedown", onClickOutside)
  }, [])

  return (
    <div ref={wrapperRef} className="relative">
      <button
        type="button"
        role="combobox"
        aria-expanded={open}
        disabled={disabled}
        onClick={() => {
          setQuery("")
          setOpen((v) => !v)
        }}
        className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
      >
        {selected ? (
          <span className="flex items-center gap-2">
            {statusIcon(selected.status)}
            {selected.name}
          </span>
        ) : (
          <span className="text-muted-foreground">{placeholder}</span>
        )}
        <ChevronsDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border border-border bg-popover p-1 shadow-md">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search agents..."
            className="mb-1 w-full rounded-md bg-background px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-ring"
          />
          <div className="max-h-60 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="px-2 py-3 text-center text-xs text-muted-foreground">
                No agents found.
              </div>
            ) : (
              filtered.map((agent) => (
                <button
                  key={agent.id}
                  type="button"
                  onClick={() => {
                    onChange(agent.id === value ? null : agent)
                    setOpen(false)
                  }}
                  className="flex w-full items-center justify-between gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-muted"
                >
                  <span className="flex items-center gap-2">
                    {statusIcon(agent.status)}
                    <span>{agent.name}</span>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {agent.status}
                  </span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function AgentStatusBadge({
  status,
}: {
  status: AgentOption["status"]
}) {
  const label: Record<AgentOption["status"], string> = {
    healthy: "Healthy",
    unhealthy: "Unhealthy",
    offline: "Offline",
    pending: "Pending",
  }
  const color: Record<AgentOption["status"], string> = {
    healthy: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
    unhealthy: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
    offline: "bg-muted text-muted-foreground",
    pending: "bg-blue-500/15 text-blue-600 dark:text-blue-400",
  }
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        color[status]
      )}
    >
      <Plug className="h-3 w-3" />
      {label[status]}
    </span>
  )
}
