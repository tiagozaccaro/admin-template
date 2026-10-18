"use client"

import { useEffect, useState } from "react"

import { Badge } from "@workspace/ui/components/badge"
import { Button } from "@workspace/ui/components/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Input } from "@workspace/ui/components/input"
import { Label } from "@workspace/ui/components/label"
import { Select } from "@workspace/ui/components/select"
import {
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@workspace/ui/components/select"
import { Skeleton } from "@workspace/ui/components/skeleton"
import { apiFetch, API_BASE_URL } from "@/src/lib/api"

interface Provider {
  id: string
  name: string
  kind: string
  model: string
  workspace_id: string | null
  user_id: string | null
  created_at: string
}

interface GenerationResult {
  id: string
  kind: string
  status: string
  workspace_id: string
  created_at: string
}

type TaskKind = "idea" | "script"

export default function GeneratePage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [taskKind, setTaskKind] = useState<TaskKind>("idea")
  const [providerId, setProviderId] = useState<string | null>(null)
  const [evidenceIds, setEvidenceIds] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)

  useEffect(() => {
    let cancelled = false
    apiFetch<Provider[]>(`/api/v1/ai/providers`)
      .then((data: Provider[]) => {
        if (!cancelled) setProviders(data)
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setResult(null)
    setSubmitting(true)
    try {
      const body: Record<string, unknown> = {
        evidence_ids: evidenceIds.split(",").map((s) => s.trim()).filter(Boolean),
        workspace_id: "00000000-0000-0000-0000-000000000000",
      }
      if (providerId) body["provider_config_id"] = providerId
      const endpoint = taskKind === "idea" ? "/api/v1/ai/ideas" : "/api/v1/ai/scripts"
      const created = await apiFetch<GenerationResult>(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      })
      setResult(created)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generation failed")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Generate Idea / Script</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>AI Generation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-4 w-3/4 rounded-full bg-muted animate-pulse" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Generate Idea / Script</h1>
        <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
          Refresh
        </Button>
      </div>
      <p className="mb-6 text-muted-foreground">
        Generate a content idea or draft script grounded in collected
        evidence, using a configured AI provider.
      </p>

      {error && (
        <div className="mb-6 rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Configure Generation</CardTitle>
          <CardDescription>
            Select a task kind, an AI provider, and the evidence to ground
            the output in.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="taskKind">Task</Label>
                <Select
                  id="taskKind"
                  value={taskKind}
                  onValueChange={(value) => setTaskKind(value as TaskKind)}
                >
                  <SelectValue />
                  <SelectContent>
                    <SelectItem value="idea">Idea</SelectItem>
                    <SelectItem value="script">Script</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="providerId">AI Provider</Label>
                <Select
                  id="providerId"
                  value={providerId ?? ""}
                  onValueChange={(value) => setProviderId(value || null)}
                >
                  <SelectValue placeholder="Select a provider…" />
                  <SelectContent>
                    {providers.map((p) => (
                      <SelectItem key={p.id} value={p.id}>
                        {p.name} ({p.model})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="evidenceIds">Evidence IDs (comma-separated)</Label>
              <Input
                id="evidenceIds"
                placeholder="e.g. 550e8400-e29b-..., 6ba7b810-..."
                value={evidenceIds}
                onChange={(e) => setEvidenceIds(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to generate without grounding evidence.
              </p>
            </div>
            <Button type="submit" disabled={submitting || providers.length === 0}>
              {submitting ? "Generating…" : `Generate ${taskKind}`}
            </Button>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card className="w-full max-w-4xl mt-6">
          <CardHeader>
            <CardTitle>Generation Result</CardTitle>
            <CardDescription>
              {result.kind} created and queued for processing.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid gap-2 md:grid-cols-4">
              <div className="bg-muted p-3 rounded">
                <div className="text-xs text-muted-foreground">ID</div>
                <div className="font-mono text-sm">{result.id}</div>
              </div>
              <div className="bg-muted p-3 rounded">
                <div className="text-xs text-muted-foreground">Kind</div>
                <div className="font-medium">{result.kind}</div>
              </div>
              <div className="bg-muted p-3 rounded">
                <div className="text-xs text-muted-foreground">Status</div>
                <Badge variant="outline">{result.status}</Badge>
              </div>
              <div className="bg-muted p-3 rounded">
                <div className="text-xs text-muted-foreground">Created</div>
                <div className="font-mono text-sm">{result.created_at}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <p className="mt-6 text-sm text-muted-foreground">
        API base: {API_BASE_URL}
      </p>
    </div>
  )
}
