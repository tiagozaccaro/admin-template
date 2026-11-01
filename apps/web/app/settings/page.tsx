"use client"

import { useCallback, useEffect, useState } from "react"

import { Models } from "@opencode-ai/models"

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@workspace/ui/components/select"
import { Checkbox } from "@workspace/ui/components/checkbox"
import { Textarea } from "@workspace/ui/components/textarea"
import { RiDeleteBinLine } from "@remixicon/react"

import { getApiUrl } from "@/lib/api"

type ProviderSettings = {
  api_key: string
  base_url: string
}

type ProviderEntry = {
  provider: string
  settings: ProviderSettings
}

type AppSettings = {
  app_name: string
  app_description: string
  maintenance_mode: boolean
  session_ttl_minutes: number
  chat_models: string[]
  provider_entries: ProviderEntry[]
}

type ProviderGroup = {
  provider: string
  models: string[]
}

type ProviderRowProps = {
  index: number
  entry: ProviderEntry
  providers: ProviderGroup[]
  onChangeProvider: (index: number, value: string) => void
  onChangeApiKey: (index: number, value: string) => void
  onChangeBaseUrl: (index: number, value: string) => void
  onRemove: (index: number) => void
}

function ProviderRow({
  index,
  entry,
  providers,
  onChangeProvider,
  onChangeApiKey,
  onChangeBaseUrl,
  onRemove,
}: ProviderRowProps) {
  const settings = entry.settings ?? { api_key: "", base_url: "" }
  const group = providers.find((p) => p.provider === entry.provider)
  const models = group ? group.models : []

  return (
    <div className="space-y-3 rounded-lg border bg-muted/50 p-4">
      <div className="flex items-center gap-3">
        <div className="flex flex-1 flex-col gap-1">
          <Label className="text-xs text-muted-foreground">Provider</Label>
          <Select
            defaultValue={entry.provider}
            onValueChange={(value) => {
              onChangeProvider(index, value ?? "")
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {providers.map((p) => (
                <SelectItem key={p.provider} value={p.provider}>
                  {p.provider}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <Label className="text-xs text-muted-foreground">API key</Label>
          <Input
            defaultValue={settings.api_key}
            onChange={(e) => onChangeApiKey(index, e.target.value)}
          />
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <Label className="text-xs text-muted-foreground">Base URL</Label>
          <Input
            defaultValue={settings.base_url}
            onChange={(e) => onChangeBaseUrl(index, e.target.value)}
          />
        </div>
        <Button
          variant="destructive"
          size="icon"
          onClick={() => onRemove(index)}
          aria-label="Remove provider"
        >
          <RiDeleteBinLine className="size-4" />
          <span className="sr-only">Remove provider</span>
        </Button>
      </div>
      {group && models.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-muted-foreground">
            Available models:
          </span>
          {models.map((modelName) => (
            <span
              key={modelName}
              className="inline-flex items-center gap-1 rounded-md border border-transparent bg-secondary/50 px-2 py-1 text-xs text-secondary-foreground"
            >
              {modelName}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

function parseChatModels(value: string): string[] {
  try {
    const parsed = JSON.parse(value)
    if (!Array.isArray(parsed)) return []
    return parsed.filter((entry): entry is string => typeof entry === "string")
  } catch {
    return []
  }
}

function stringifyChatModels(models: string[]): string {
  return JSON.stringify(models)
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [providers, setProviders] = useState<ProviderGroup[]>([])
  const [modelsDevLoading, setModelsDevLoading] = useState(true)
  const [modelsDevError, setModelsDevError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function bootstrap() {
      try {
        const client = Models.make()
        const [settingsRes, providerMap] = await Promise.all([
          fetch(`${getApiUrl()}/api/v1/settings`, {
            credentials: "include",
          }),
          client.providers(),
        ])

        if (!settingsRes.ok) {
          throw new Error(`Request failed (${settingsRes.status})`)
        }
        const data = (await settingsRes.json()) as {
          app_name: string
          app_description: string
          maintenance_mode: boolean
          session_ttl_minutes: number
          chat_models: string
          provider_settings: string
        }

        if (!providerMap || typeof providerMap !== "object") {
          throw new Error("Unexpected models.dev providers response")
        }

        const providerGroups: ProviderGroup[] = Object.values(
          providerMap as Record<
            string,
            { id: string; models: Record<string, unknown> }
          >
        )
          .map((provider) => ({
            provider: provider.id,
            models: Object.keys(provider.models).sort(),
          }))
          .sort((a, b) => a.provider.localeCompare(b.provider))

        const savedProviderSettings: Record<string, ProviderSettings> =
          typeof data.provider_settings === "string"
            ? (JSON.parse(data.provider_settings) as Record<
                string,
                ProviderSettings
              >)
            : {}

        const provider_entries: ProviderEntry[] = Object.entries(
          savedProviderSettings
        ).map(([provider, settings]) => ({
          provider,
          settings,
        }))

        if (!cancelled) {
          setProviders(providerGroups)
          setModelsDevLoading(false)
          setSettings({
            app_name: data.app_name,
            app_description: data.app_description,
            maintenance_mode: data.maintenance_mode,
            session_ttl_minutes: data.session_ttl_minutes,
            chat_models: parseChatModels(data.chat_models),
            provider_entries,
          })
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setModelsDevError(
            err instanceof Error
              ? err.message
              : "Failed to load models.dev data"
          )
          setModelsDevLoading(false)
          setError(
            err instanceof Error ? err.message : "Failed to load settings"
          )
        }
      }
    }

    bootstrap()
    return () => {
      cancelled = true
    }
  }, [])

  const addProvider = useCallback(() => {
    setSettings((s) => {
      if (!s) return null
      const next: ProviderEntry = {
        provider: "",
        settings: { api_key: "", base_url: "" },
      }
      return {
        ...s,
        provider_entries: [...(s.provider_entries ?? []), next],
      }
    })
  }, [])

  const removeProvider = useCallback((index: number) => {
    setSettings((s) => {
      if (!s) return null
      const next = [...(s.provider_entries ?? [])]
      next.splice(index, 1)
      return {
        ...s,
        provider_entries: next,
      }
    })
  }, [])

  const onChangeProvider = useCallback((index: number, value: string) => {
    setSettings((s) => {
      if (!s) return null
      const next = [...(s.provider_entries ?? [])]
      next[index] = {
        ...(next[index] ?? {
          provider: "",
          settings: { api_key: "", base_url: "" },
        }),
        provider: value,
      }
      return { ...s, provider_entries: next }
    })
  }, [])

  const onChangeApiKey = useCallback((index: number, value: string) => {
    setSettings((s) => {
      if (!s) return null
      const next = [...(s.provider_entries ?? [])]
      next[index] = {
        ...(next[index] ?? {
          provider: "",
          settings: { api_key: "", base_url: "" },
        }),
        settings: {
          ...(next[index]?.settings ?? { api_key: "", base_url: "" }),
          api_key: value,
        },
      }
      return { ...s, provider_entries: next }
    })
  }, [])

  const onChangeBaseUrl = useCallback((index: number, value: string) => {
    setSettings((s) => {
      if (!s) return null
      const next = [...(s.provider_entries ?? [])]
      next[index] = {
        ...(next[index] ?? {
          provider: "",
          settings: { api_key: "", base_url: "" },
        }),
        settings: {
          ...(next[index]?.settings ?? { api_key: "", base_url: "" }),
          base_url: value,
        },
      }
      return { ...s, provider_entries: next }
    })
  }, [])

  async function handleSave(event: React.FormEvent) {
    event.preventDefault()
    if (!settings) return

    setSaving(true)
    setSaved(false)
    setError(null)

    const entries = settings.provider_entries ?? []
    const provider_settings: Record<string, ProviderSettings> = {}
    const chat_models: string[] = []

    for (const entry of entries) {
      if (!entry.provider || !entry.settings) continue
      provider_settings[entry.provider] = entry.settings
      chat_models.push(entry.provider)
    }

    try {
      const res = await fetch(`${getApiUrl()}/api/v1/settings`, {
        method: "POST",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          app_name: settings.app_name,
          app_description: settings.app_description,
          maintenance_mode: settings.maintenance_mode,
          session_ttl_minutes: settings.session_ttl_minutes,
          chat_models: stringifyChatModels(chat_models),
          provider_settings: JSON.stringify(provider_settings),
        }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      setSaved(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save settings")
    } finally {
      setSaving(false)
    }
  }

  if (modelsDevLoading) {
    return (
      <div className="flex flex-col gap-6 px-4 py-6 md:gap-8 lg:px-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="mt-1 text-muted-foreground">
            Loading models from models.dev…
          </p>
        </div>
      </div>
    )
  }

  if (modelsDevError || error) {
    return (
      <div className="flex flex-col gap-6 px-4 py-6 md:gap-8 lg:px-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="mt-1 text-muted-foreground">
            Configure application and chat provider settings.
          </p>
        </div>
        <Card className="border-destructive bg-destructive/10">
          <CardContent className="py-3">
            <p className="text-sm text-destructive">
              {modelsDevError || error || "Failed to load settings"}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!settings) {
    return (
      <div className="flex flex-col gap-6 px-4 py-6 md:gap-8 lg:px-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="mt-1 text-muted-foreground">
            Configure application and chat provider settings.
          </p>
        </div>
        <p className="animate-pulse text-muted-foreground">Loading…</p>
      </div>
    )
  }

  const entries = settings.provider_entries ?? []

  return (
    <div className="flex flex-col gap-6 px-4 py-6 md:gap-8 lg:px-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-muted-foreground">
          Configure application and chat provider settings.
        </p>
      </div>

      <Card className="border">
        <CardHeader>
          <CardTitle>Application</CardTitle>
          <CardDescription>
            Core application metadata and behavior.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="app-name">App name</Label>
            <Input
              id="app-name"
              defaultValue={settings.app_name}
              onChange={(e) =>
                setSettings((s) =>
                  s ? { ...s, app_name: e.target.value } : null
                )
              }
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="app-description">App description</Label>
            <Textarea
              id="app-description"
              rows={2}
              defaultValue={settings.app_description}
              onChange={(e) =>
                setSettings((s) =>
                  s ? { ...s, app_description: e.target.value } : null
                )
              }
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="session-ttl">Session TTL (minutes)</Label>
            <Input
              id="session-ttl"
              type="number"
              defaultValue={String(settings.session_ttl_minutes)}
              onChange={(e) =>
                setSettings((s) =>
                  s
                    ? {
                        ...s,
                        session_ttl_minutes: Number(e.target.value) || 0,
                      }
                    : null
                )
              }
            />
          </div>
          <div className="flex items-center gap-2">
            <Checkbox
              id="maintenance-mode"
              checked={settings.maintenance_mode}
              onCheckedChange={(checked) =>
                setSettings((s) =>
                  s ? { ...s, maintenance_mode: checked } : null
                )
              }
            />
            <Label htmlFor="maintenance-mode">Maintenance mode</Label>
          </div>
        </CardContent>
      </Card>

      <Card className="border">
        <CardHeader>
          <CardTitle>Chat providers</CardTitle>
          <CardDescription>
            Add the providers the agent can use. Each provider gets its own API
            key and base URL. Models are listed from models.dev.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {entries.map((entry, index) => (
              <ProviderRow
                key={index}
                index={index}
                entry={entry}
                providers={providers}
                onChangeProvider={onChangeProvider}
                onChangeApiKey={onChangeApiKey}
                onChangeBaseUrl={onChangeBaseUrl}
                onRemove={removeProvider}
              />
            ))}
            <div className="flex gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={addProvider}
                disabled={saving || providers.length === 0}
              >
                Add provider
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-3">
        <Button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save changes"}
        </Button>
        {saved && (
          <span className="inline-flex items-center gap-1 rounded-md border border-green-100 bg-green-50/50 px-2 py-1 text-xs font-medium text-green-700">
            Saved.
          </span>
        )}
      </div>
    </div>
  )
}
