"use client"

import { useEffect, useState } from "react"

import { Badge } from "@workspace/ui/components/badge"
import { Skeleton } from "@workspace/ui/components/skeleton"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { apiFetch } from "@/src/lib/api"

interface JobDetail {
  id: string
  workspace_id: string
  kind: string
  status: string
  created_at: string
  started_at: string | null
  finished_at: string | null
  error_code: string | null
}

export default function JobPage({ params }: { params: { id: string } }) {
  const [job, setJob] = useState<JobDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    apiFetch<JobDetail>(`/api/v1/jobs/${params.id}`)
      .then((data: JobDetail) => {
        if (!cancelled) setJob(data)
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
        <h1 className="mb-6 text-2xl font-semibold">Job</h1>
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
        <h1 className="mb-6 text-2xl font-semibold">Job</h1>
        <Card className="w-full max-w-4xl">
          <CardContent>
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Job</h1>
        <Card className="w-full max-w-4xl">
          <CardContent>Loading job…</CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-6 text-2xl font-semibold">Job Status</h1>
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Job {job.id}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Badge variant={job.status === "completed" ? "default" : "secondary"}>
                {job.status}
              </Badge>
            </div>
            <div>
              <dt className="text-sm font-medium">Kind</dt>
              <dd className="text-sm">{job.kind}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">Workspace</dt>
              <dd className="text-sm">{job.workspace_id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">Created at</dt>
              <dd className="text-sm">{job.created_at}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">Started at</dt>
              <dd className="text-sm">{job.started_at ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium">Finished at</dt>
              <dd className="text-sm">{job.finished_at ?? "—"}</dd>
            </div>
            {job.error_code && (
              <div className="col-span-2">
                <dt className="text-sm font-medium text-destructive">Error</dt>
                <dd className="text-sm text-destructive">{job.error_code}</dd>
              </div>
            )}
          </dl>
        </CardContent>
      </Card>
    </div>
  )
}
