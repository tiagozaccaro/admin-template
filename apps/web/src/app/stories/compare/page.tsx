"use client"

import { useEffect, useState } from "react"

import { Badge } from "@workspace/ui/components/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Separator } from "@workspace/ui/components/separator"
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

interface CompareResponse {
  story_a: Story
  story_b: Story
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

function sourceLabel(source: StorySource | null) {
  if (!source) return "—"
  try {
    return new URL(source.url).hostname
  } catch {
    return source.url
  }
}

/** High-level fields worth comparing between two stories. */
const COMPARE_FIELDS: { key: string; label: string }[] = [
  { key: "title", label: "Title" },
  { key: "source", label: "Source" },
  { key: "published_at", label: "Published" },
  { key: "discovered_at", label: "Discovered" },
]

function fieldValues(story: Story) {
  return {
    title: story.title,
    source: sourceLabel(story.source),
    published_at: formatDate(story.published_at),
    discovered_at: formatDate(story.discovered_at),
  }
}

function valuesDiffer(a: unknown, b: unknown) {
  return String(a) !== String(b)
}

export default function ComparePage() {
  const [aId, setAId] = useState<string>("")
  const [bId, setBId] = useState<string>("")
  const [compare, setCompare] = useState<CompareResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!aId || !bId) {
      setCompare(null)
      return
    }
    setLoading(true)
    apiFetch<CompareResponse>(
      `/api/v1/stories/compare?story_a_id=${encodeURIComponent(
        aId
      )}&story_b_id=${encodeURIComponent(bId)}`
    )
      .then((data) => {
        if (!cancelled) setCompare(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [aId, bId])

  const storyA = compare?.story_a
  const storyB = compare?.story_b
  const fieldsA = storyA ? fieldValues(storyA) : {}
  const fieldsB = storyB ? fieldValues(storyB) : {}

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Compare Stories</h1>
        <div className="flex gap-2">
          <input
            className="rounded-md border px-3 py-2 text-sm"
            placeholder="Story A id"
            value={aId}
            onChange={(e) => setAId(e.target.value)}
          />
          <input
            className="rounded-md border px-3 py-2 text-sm"
            placeholder="Story B id"
            value={bId}
            onChange={(e) => setBId(e.target.value)}
          />
          <ButtonLoader
            loading={loading}
            disabled={!aId || !bId || loading}
            onClick={() => {
              window.location.reload()
            }}
          >
            Compare
          </ButtonLoader>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex h-96 items-center justify-center">
          <p className="text-muted-foreground">Comparing…</p>
        </div>
      ) : storyA && storyB ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <StoryCard
            label="Story A"
            story={storyA}
            values={fieldsA}
            other={fieldsB}
          />
          <Separator orientation="vertical" className="self-stretch" />
          <StoryCard
            label="Story B"
            story={storyB}
            values={fieldsB}
            other={fieldsA}
          />
        </div>
      ) : (
        <div className="rounded-md border border-muted p-8 text-center text-muted-foreground">
          Enter two story IDs to compare them side by side.
        </div>
      )}
      <p className="mt-6 text-sm text-muted-foreground">
        API base: {API_BASE_URL}
      </p>
    </div>
  )
}

function ButtonLoader({
  loading,
  disabled,
  onClick,
  children,
}: {
  loading: boolean
  disabled: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      className="inline-flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors hover:bg-muted focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:outline-none disabled:pointer-events-none disabled:opacity-50"
      disabled={disabled}
      onClick={onClick}
    >
      {loading ? (
        <span className="flex h-4 w-4">
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </span>
      ) : (
        children
      )}
    </button>
  )
}

function StoryCard({
  label,
  story,
  values,
  other,
}: {
  label: string
  story: Story
  values: Record<string, string>
  other: Record<string, string>
}) {
  return (
    <Card className="flex h-full flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {label}
          <span className="ml-auto text-xs text-muted-foreground">
            {story.id.slice(0, 8)}…
          </span>
        </CardTitle>
        <CardDescription>{story.canonical_url}</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 space-y-4">
        {COMPARE_FIELDS.map((field) => {
          const differ =
            valuesDiffer(values[field.key], other[field.key]) &&
            values[field.key] !== undefined
          return (
            <div
              key={field.key}
              className={cn(
                "flex items-start gap-3 rounded-md border p-3 transition-colors",
                differ
                  ? "border-yellow-300/50 bg-yellow-50/50"
                  : "border-transparent"
              )}
            >
              <span className="mt-0.5 shrink-0 text-xs font-medium text-muted-foreground">
                {field.label}
              </span>
              <div className="flex-1 text-sm leading-relaxed">
                {values[field.key] ?? "—"}
              </div>
              {differ && (
                <span
                  className="text-xs text-yellow-500"
                  title="Differs from other story"
                >
                  ↕
                </span>
              )}
            </div>
          )
        })}
        <div className="border-t pt-2">
          <span className="mb-1 block text-xs text-muted-foreground">
            Raw payload
          </span>
          <pre className="max-h-40 overflow-auto rounded bg-muted/50 p-2 text-xs text-muted-foreground">
            {JSON.stringify(story.raw_payload ?? null, null, 2)}
          </pre>
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between">
        <Badge variant="outline">
          {story.source?.type?.toUpperCase() ?? "—"}
        </Badge>
        <a
          href={story.canonical_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-primary hover:underline"
        >
          Open source
        </a>
      </CardFooter>
    </Card>
  )
}
