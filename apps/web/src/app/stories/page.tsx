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
import { Skeleton } from "@workspace/ui/components/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { cn } from "@workspace/ui/lib/utils"
import { apiFetch, API_BASE_URL } from "@/src/lib/api"

interface StorySource {
  id: string
  type: string
  url: string
}

interface Story {
  id: string
  source_id: string
  source: StorySource | null
  canonical_url: string
  title: string
  published_at: string | null
  discovered_at: string
  raw_payload: Record<string, unknown> | null
  embedding: number[] | null
}

function formatDate(value: string | null) {
  if (!value) return "—"
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function sourceHostname(url: string | undefined) {
  if (!url) return "—"
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}

export default function StoriesPage() {
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    apiFetch<Story[]>(`/api/v1/stories`)
      .then((data: Story[]) => {
        if (!cancelled) setStories(data)
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

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Discover Stories</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Stories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-5 w-3/4" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/2" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/3" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/3" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/3" />
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
        <h1 className="mb-6 text-2xl font-semibold">Discover Stories</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Stories</CardTitle>
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
        <h1 className="text-2xl font-semibold">Discover Stories</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.location.reload()}
        >
          Refresh
        </Button>
      </div>
      <p className="mb-6 text-muted-foreground">
        Ranked stories from your connected sources, most recently discovered
        first.
      </p>
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Stories</CardTitle>
          <CardDescription>
            {stories.length} story{stories.length !== 1 ? "s" : ""} discovered
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/3">Title</TableHead>
                <TableHead>Source</TableHead>
                <TableHead className="w-1/6">Type</TableHead>
                <TableHead className="w-1/6">Published</TableHead>
                <TableHead className="w-1/6">Discovered</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stories.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="py-4 text-center text-muted-foreground"
                  >
                    No stories discovered yet. Connect a source to begin.
                  </TableCell>
                </TableRow>
              ) : (
                stories.map((story) => (
                  <TableRow key={story.id}>
                    <TableCell className="font-medium">{story.title}</TableCell>
                    <TableCell>
                      {story.source ? (
                        <div className="flex items-center gap-2">
                          <span
                            className="truncate text-xs text-muted-foreground"
                            title={story.source.url}
                          >
                            {sourceHostname(story.source.url)}
                          </span>
                          <Badge variant="outline">
                            {story.source.type.toUpperCase()}
                          </Badge>
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {story.source?.type ?? "—"}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDate(story.published_at)}</TableCell>
                    <TableCell>{formatDate(story.discovered_at)}</TableCell>
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
