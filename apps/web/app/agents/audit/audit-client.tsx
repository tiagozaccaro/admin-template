"use client"

import * as React from "react"
import { RefreshCw } from "lucide-react"

import { cn } from "@workspace/ui/lib/utils"
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
import {
  LoadingState,
  ErrorState,
  EmptyState,
} from "../../../components/states"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type AuditEntry = {
  id: string
  tenant_id: string
  user_id: string
  agent_id: string
  tool_name: string
  args: Record<string, unknown> | null
  result_summary: string | null
  status: string
  created_at: string
}

async function fetchAudit(): Promise<AuditEntry[]> {
  const res = await fetch(`${API_URL}/api/v1/agents/audit`, {
    cache: "no-store",
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch audit log (${res.status})`)
  }
  return res.json()
}

export function AuditClient() {
  const [entries, setEntries] = React.useState<AuditEntry[] | null>(null)
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(true)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchAudit()
      setEntries(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit log")
      setEntries([])
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    load()
  }, [load])

  if (loading) {
    return <LoadingState label="Loading audit log..." />
  }

  if (error) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <ErrorState message={error} />
        <Button variant="outline" onClick={load}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Audit log</h1>
          <p className="text-sm text-muted-foreground">
            Review every tool invocation executed by registered agents.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Audit entries</CardTitle>
          <CardDescription>
            {entries?.length ?? 0} recorded tool invocation(s).
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!entries || entries.length === 0 ? (
            <EmptyState
              title="No audit entries"
              description="Tool invocations will appear here as agents run them."
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Tool</TableHead>
                  <TableHead>Agent</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Summary</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell className="whitespace-nowrap text-muted-foreground">
                      {new Date(entry.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {entry.tool_name}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {entry.agent_id.slice(0, 8)}
                    </TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                          entry.status === "ok"
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                            : entry.status === "error"
                              ? "bg-destructive/15 text-destructive"
                              : "bg-muted text-muted-foreground"
                        )}
                      >
                        {entry.status}
                      </span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {entry.result_summary ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
