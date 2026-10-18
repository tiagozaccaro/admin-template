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
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@workspace/ui/components/table"
import { apiFetch, API_BASE_URL } from "@/src/lib/api"

interface EvidenceItem {
  id: string
  workspace_id: string
  story_id: string | null
  collected_by: string
  kind: string
  content: string
  span: Record<string, unknown> | null
  created_at: string
}

interface KindOption {
  label: string
  value: string
}

const KIND_OPTIONS: KindOption[] = [
  { label: "Quote", value: "quote" },
  { label: "Excerpt", value: "excerpt" },
  { label: "Link", value: "link" },
]

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [storyId, setStoryId] = useState("")
  const [kind, setKind] = useState<string>("quote")
  const [content, setContent] = useState("")
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let cancelled = false
    apiFetch<EvidenceItem[]>(`/api/v1/evidence`)
      .then((data: EvidenceItem[]) => {
        if (!cancelled) setEvidence(data)
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

  async function handleCollect(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const body: Record<string, unknown> = {
        kind,
        content,
      }
      if (storyId) body["story_id"] = storyId
      await apiFetch<EvidenceItem>("/api/v1/evidence", {
        method: "POST",
        body: JSON.stringify(body),
      })
      setContent("")
      setStoryId("")
      setKind("quote")
      // Refresh list
      const updated = await apiFetch<EvidenceItem[]>(`/api/v1/evidence`)
      setEvidence(updated as unknown as EvidenceItem[])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to collect evidence")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Collect Evidence</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Evidence</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-5 w-3/4" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/2" />
                </TableCell>
              </TableRow>
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Collect Evidence</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Evidence</CardTitle>
          </CardHeader>
          <CardContent className="text-destructive">{error}</CardContent>
          <CardContent>
            <Button variant="outline" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Collect Evidence</h1>
        <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
          Refresh
        </Button>
      </div>
      <p className="mb-6 text-muted-foreground">
        Collect quotes, excerpts, and links from stories. Each item is
        attributed to its original source and your workspace.
      </p>

      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>New Evidence</CardTitle>
          <CardDescription>
            Save a quote, excerpt, or link with source attribution.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCollect} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="kind">Kind</Label>
                <Select
                  id="kind"
                  value={kind}
                  onValueChange={(value) => {
                    setKind(value as string)
                  }}
                >
                  <SelectValue />
                  <SelectContent>
                    {KIND_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="storyId">Story ID (optional)</Label>
                <Input
                  id="storyId"
                  placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
                  value={storyId}
                  onChange={(e) => setStoryId(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="content">Content</Label>
              <Input
                id="content"
                placeholder="Paste a quote, excerpt, or link here"
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={submitting || !content}>
              {submitting ? "Collecting…" : "Collect Evidence"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="w-full max-w-4xl mt-6">
        <CardHeader>
          <CardTitle>Collected Evidence</CardTitle>
          <CardDescription>{evidence.length} item(s) collected</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/4">Kind</TableHead>
                <TableHead>Content</TableHead>
                <TableHead className="w-1/6">Story</TableHead>
                <TableHead className="w-1/6">Collected</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evidence.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="py-4 text-center text-muted-foreground"
                  >
                    No evidence collected yet.
                  </TableCell>
                </TableRow>
              ) : (
                evidence.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Badge variant="outline">{item.kind}</Badge>
                    </TableCell>
                    <TableCell className="max-w-[300px] truncate">
                      {item.content}
                    </TableCell>
                    <TableCell>
                      {item.story_id ? item.story_id.slice(0, 8) + "…" : "—"}
                    </TableCell>
                    <TableCell>
                      {new Date(item.created_at).toLocaleString(undefined, {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <p className="mt-6 text-sm text-muted-foreground">
        API base: {API_BASE_URL}
      </p>
    </div>
  )
}
