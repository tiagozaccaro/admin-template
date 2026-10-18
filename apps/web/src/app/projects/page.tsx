"use client"

import { useEffect, useState } from "react"

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
import { Skeleton } from "@workspace/ui/components/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { apiFetch } from "@/src/lib/api"

interface ProjectItem {
  id: string
  workspace_id: string
  name: string
  created_by: string
  created_at: string
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [name, setName] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const WORKSPACE_ID = "00000000-0000-0000-000000000000"

  useEffect(() => {
    let cancelled = false
    apiFetch<ProjectItem[]>(
      `/api/v1/projects?workspace_id=${WORKSPACE_ID}`
    )
      .then((data: ProjectItem[]) => {
        if (!cancelled) setProjects(data)
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

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await apiFetch<ProjectItem>("/api/v1/projects", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: WORKSPACE_ID,
          name,
          created_by: WORKSPACE_ID,
        }),
      })
      setName("")
      const updated = await apiFetch<ProjectItem[]>(
        `/api/v1/projects?workspace_id=${WORKSPACE_ID}`
      )
      setProjects(updated as unknown as ProjectItem[])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create project")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <h1 className="mb-6 text-2xl font-semibold">Projects</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-5 w-1/2" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-1/4" />
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
        <h1 className="mb-6 text-2xl font-semibold">Projects</h1>
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-6 text-2xl font-semibold">Projects</h1>

      <Card className="w-full max-w-4xl mb-6">
        <CardHeader>
          <CardTitle>Create Project</CardTitle>
          <CardDescription>
            Organize ideas, scripts, and drafts into a named collection.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Project name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Q3 Blog Series"
                disabled={submitting}
              />
            </div>
            <Button type="submit" disabled={submitting}>
              Create project
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Your projects</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Created by</TableCell>
                <TableCell>Created at</TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell>{project.name}</TableCell>
                  <TableCell>{project.created_by}</TableCell>
                  <TableCell>{project.created_at}</TableCell>
                </TableRow>
              ))}
              {projects.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3}>No projects yet. Create one above.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
