"use client"

import * as React from "react"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
import { Button } from "@workspace/ui/components/button"
import { AgentProvider } from "@workspace/ui/components/ai-elements/agent-provider"
import { AgentChat } from "@workspace/ui/components/ai-elements/agent-chat"
import type { AgentAdapter } from "@workspace/ui/lib/agent-adapter"
import type { Session } from "@workspace/ui/hooks/use-sessions"
import { useSessions } from "@workspace/ui/hooks/use-sessions"

export function AgentTabs({ adapter }: { adapter: AgentAdapter }) {
  const { sessions, active, setActive, create, remove } = useSessions([
    { id: "default", title: "Chat 1" },
  ])

  return (
    <div className="flex h-full min-h-0 flex-col">
      <Tabs
        value={active ?? sessions[0]?.id ?? "default"}
        onValueChange={setActive}
        className="flex min-h-0 flex-1 flex-col"
      >
        <TabsList>
          {sessions.map((s: Session) => (
            <TabsTrigger key={s.id} value={s.id}>
              {s.title}
              <span
                className="ml-2 cursor-pointer text-xs"
                onClick={() => remove(s.id)}
              >
                ×
              </span>
            </TabsTrigger>
          ))}
          <Button size="sm" variant="ghost" onClick={() => create()}>
            +
          </Button>
        </TabsList>
        {sessions.map((s: Session) => (
          <TabsContent
            key={s.id}
            value={s.id}
            className="flex min-h-0 flex-1 flex-col"
          >
            <AgentProvider sessionId={s.id} adapter={adapter}>
              <AgentChat />
            </AgentProvider>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
