"use client"

import { useEffect, useState } from "react"

import { Badge } from "@workspace/ui/components/badge"
import { Skeleton } from "@workspace/ui/components/skeleton"
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
import { apiFetch } from "@/src/lib/api"

interface RevisionItem {
  revision: number
  author_id: string
  created_at: string
  payload: Record<string, unknown>
  prior_revision_id: string | null
}

interface DraftDetail {
  id: string
  content_item_id: string
  current_revision_id: string | null
  updated_at: string
  revisions: RevisionItem[]
}

export default function DraftPage({ params }: { params: { id: string } }) {
  const [draft, setDraft] = useState<DraftDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    apiFetch<DraftDetail>(`/api/v1/drafts/${params.id}`)
      .then((data: DraftDetail) => {
        if (!cancelled) setDraft(data)
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
  }, [params.id])

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Draft</h1>
        <Card className="w-full max-w-4xl">
          <CardContent className="space-y-2">
            <div className="h-5 w-1/3"><Skeleton /></div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Draft</h1>
        <Card className="w-full max-w-4xl">
          <CardContent>
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!draft) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Draft</h1>
        <Card className="w-full max-w-4xl">
          <CardContent>Loading draft…</CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-6 text-2xl font-semibold">Draft Version History</h1>
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Draft {draft.id}</CardTitle>
          <CardDescription>
            Content item {draft.content_item_id}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4">
            Current revision:{draft.current_revision_id ?? "none"} &nbsp;|&nbsp;
            Updated: {draft.updated_at}
          </p>
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell>Revision</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Created at</TableCell>
                <TableCell>Prior revision</TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {draft.revisions.map((rev) => (
                <TableRow key={`${rev.revision}`}>
                  <TableCell>{rev.revision}</TableCell>
                  <TableCell>{rev.author_id}</TableCell>
                  <TableCell>{rev.created_at}</TableCell>
                  <TableCell>{rev.prior_revision_id ?? "—"}</TableCell>
                </TableRow>
              ))}
              {draft.revisions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4}>No revisions yet.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
