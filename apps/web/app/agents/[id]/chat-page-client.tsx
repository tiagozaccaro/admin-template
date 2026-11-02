"use client"

import * as React from "react"
import { ArrowLeft, Plug, RefreshCw, Server } from "lucide-react"

import { AgentChat } from "../../../components/chat"
import {
  AgentSelector,
  type AgentOption,
} from "../../../components/agent-selector"
import { Button } from "@workspace/ui/components/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { LoadingState, ErrorState } from "../../../components/states"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type Agent = {
  id: string
  name: string
  url: string
  status: "healthy" | "unhealthy" | "offline" | "pending"
}

async function fetchAgents(): Promise<Agent[]> {
  const res = await fetch(`${API_URL}/api/v1/agents`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`Failed to fetch agents (${res.status})`)
  }
  return res.json()
}

async function fetchAgent(id: string): Promise<Agent> {
  const res = await fetch(`${API_URL}/api/v1/agents/${id}`, {
    cache: "no-store",
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch agent (${res.status})`)
  }
  return res.json()
}

export function ChatPageClient({ agentId }: { agentId: string }) {
  const [agents, setAgents] = React.useState<Agent[] | null>(null)
  const [selectedId, setSelectedId] = React.useState<string | null>(agentId)
  const [selected, setSelected] = React.useState<Agent | null>(null)
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(true)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchAgents()
      setAgents(data)
      const current = await fetchAgent(agentId)
      setSelected(current)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load agent")
    } finally {
      setLoading(false)
    }
  }, [agentId])

  React.useEffect(() => {
    load()
  }, [load])

  React.useEffect(() => {
    setSelectedId(agentId)
  }, [agentId])

  const options: AgentOption[] = React.useMemo(
    () =>
      (agents ?? []).map((a) => ({
        id: a.id,
        name: a.name,
        url: a.url,
        status: a.status,
      })),
    [agents]
  )

  if (loading) {
    return <LoadingState label="Loading agent..." />
  }

  if (error || !selected) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <ErrorState message={error || "Agent not found"} />
        <Button variant="outline" onClick={load}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center gap-4 border-b p-4">
        <Button render={<a href="/agents" />} variant="ghost" size="sm">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Agents
        </Button>
        <div className="flex flex-1 items-center gap-3">
          <Server className="h-5 w-5 text-muted-foreground" />
          <div className="flex flex-col">
            <span className="text-sm font-medium">{selected.name}</span>
            <span className="text-xs text-muted-foreground">
              {selected.url}
            </span>
          </div>
        </div>
        <AgentSelector
          agents={options}
          value={selectedId}
          onChange={(agent) => {
            if (agent) {
              window.history.replaceState(null, "", `/agents/${agent.id}`)
            }
          }}
          placeholder="Switch agent..."
        />
      </header>
      <main className="flex-1 overflow-hidden">
        <AgentChat agentUrl={selected.url} />
      </main>
    </div>
  )
}
