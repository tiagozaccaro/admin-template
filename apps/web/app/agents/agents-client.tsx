"use client"

import * as React from "react"
import { Plug, RefreshCw, Server } from "lucide-react"

import {
  AgentSelector,
  type AgentOption,
} from "../../components/agent-selector"
import { RegisterAgentForm } from "../../components/register-agent-form"
import { Button } from "@workspace/ui/components/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { LoadingState, ErrorState, EmptyState } from "../../components/states"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type Agent = {
  id: string
  name: string
  url: string
  status: "healthy" | "unhealthy" | "offline" | "pending"
  capabilities: Record<string, unknown> | null
  last_seen_at: string | null
}

async function fetchAgents(): Promise<Agent[]> {
  const res = await fetch(`${API_URL}/api/v1/agents`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`Failed to fetch agents (${res.status})`)
  }
  return res.json()
}

async function registerAgent(values: {
  name: string
  url: string
  token: string
  capabilities: string
}): Promise<Agent> {
  const res = await fetch(`${API_URL}/api/v1/agents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: values.name,
      url: values.url,
      token: values.token || undefined,
      capabilities: values.capabilities
        ? JSON.parse(values.capabilities)
        : undefined,
    }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data?.detail || `Registration failed (${res.status})`)
  }
  return res.json()
}

async function deleteAgent(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/agents/${id}`, {
    method: "DELETE",
  })
  if (!res.ok) {
    throw new Error(`Delete failed (${res.status})`)
  }
}

async function healthCheckAgent(id: string): Promise<Agent> {
  const res = await fetch(`${API_URL}/api/v1/agents/${id}/health`, {
    method: "POST",
  })
  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`)
  }
  return res.json()
}

export function AgentsClient() {
  const [agents, setAgents] = React.useState<Agent[] | null>(null)
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [registering, setRegistering] = React.useState(false)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchAgents()
      setAgents(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load agents")
      setAgents([])
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    load()
  }, [load])

  async function handleRegister(values: {
    name: string
    url: string
    token: string
    capabilities: string
  }) {
    setRegistering(true)
    try {
      await registerAgent(values)
      await load()
    } finally {
      setRegistering(false)
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteAgent(id)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed")
    }
  }

  async function handleHealthCheck(id: string) {
    try {
      await healthCheckAgent(id)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Health check failed")
    }
  }

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

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Agents</h1>
          <p className="text-sm text-muted-foreground">
            Register and manage standalone machine admin agents.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <RegisterAgentForm onSubmit={handleRegister} disabled={registering} />
        </div>
      </div>

      {error && <ErrorState message={error} />}

      {loading ? (
        <LoadingState label="Loading agents..." />
      ) : agents && agents.length === 0 ? (
        <EmptyState
          title="No agents registered"
          description="Register a standalone agent daemon to begin."
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Registered agents</CardTitle>
            <CardDescription>
              {agents?.length ?? 0} agent(s) for your tenant.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last seen</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(agents ?? []).map((agent) => (
                  <TableRow key={agent.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Server className="h-4 w-4 text-muted-foreground" />
                        {agent.name}
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {agent.url}
                    </TableCell>
                    <TableCell>
                      <AgentSelector
                        agents={options}
                        value={agent.id}
                        onChange={() => {}}
                        disabled
                        placeholder=""
                      />
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {agent.last_seen_at
                        ? new Date(agent.last_seen_at).toLocaleString()
                        : "never"}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleHealthCheck(agent.id)}
                        >
                          <Plug className="h-4 w-4" />
                          Check
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(agent.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
