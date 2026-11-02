"use client"

import * as React from "react"
import { Plug, Plus } from "lucide-react"

import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Label } from "@workspace/ui/components/label"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@workspace/ui/components/sheet"
import { Textarea } from "@workspace/ui/components/textarea"

export type RegisterAgentFormValues = {
  name: string
  url: string
  token: string
  capabilities: string
}

type RegisterAgentFormProps = {
  onSubmit: (values: RegisterAgentFormValues) => Promise<void> | void
  disabled?: boolean
  initial?: Partial<RegisterAgentFormValues>
  triggerLabel?: string
}

export function RegisterAgentForm({
  onSubmit,
  disabled,
  initial,
  triggerLabel = "Register agent",
}: RegisterAgentFormProps) {
  const [open, setOpen] = React.useState(false)
  const [name, setName] = React.useState(initial?.name ?? "")
  const [url, setUrl] = React.useState(initial?.url ?? "")
  const [token, setToken] = React.useState(initial?.token ?? "")
  const [capabilities, setCapabilities] = React.useState(
    initial?.capabilities ?? ""
  )
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await onSubmit({ name, url, token, capabilities })
      setOpen(false)
      setName("")
      setUrl("")
      setToken("")
      setCapabilities("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger
        render={
          <Button disabled={disabled}>
            <Plus className="mr-2 h-4 w-4" />
            {triggerLabel}
          </Button>
        }
      />
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Register a new agent</SheetTitle>
          <SheetDescription>
            Provide the agent daemon URL and bearer token. The agent will be
            health-checked on registration.
          </SheetDescription>
        </SheetHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="agent-name">Name</Label>
            <Input
              id="agent-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="prod-agent-1"
              disabled={submitting}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="agent-url">URL</Label>
            <Input
              id="agent-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://agent.example.com"
              disabled={submitting}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="agent-token">Bearer token</Label>
            <Input
              id="agent-token"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="agent-bearer-token"
              disabled={submitting}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="agent-capabilities">Capabilities (JSON)</Label>
            <Textarea
              id="agent-capabilities"
              value={capabilities}
              onChange={(e) => setCapabilities(e.target.value)}
              placeholder='{"streaming": true}'
              disabled={submitting}
              className="font-mono text-xs"
            />
          </div>
          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          <SheetFooter>
            <SheetClose
              render={
                <Button type="button" variant="outline" disabled={submitting}>
                  Cancel
                </Button>
              }
            />
            <Button type="submit" disabled={submitting}>
              {submitting ? "Registering..." : "Register"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  )
}
