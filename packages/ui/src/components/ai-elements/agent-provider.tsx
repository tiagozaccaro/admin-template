"use client"

import * as React from "react"
import type {
  AgentAdapter,
  AgentMessage,
} from "@workspace/ui/lib/agent-adapter"

type Ctx = {
  sessionId: string
  adapter: AgentAdapter
  messages: AgentMessage[]
  send: (text: string) => Promise<void>
  isStreaming: boolean
}

const AgentContext = React.createContext<Ctx | null>(null)

export function AgentProvider({
  sessionId,
  adapter,
  initialMessages = [],
  children,
}: {
  sessionId: string
  adapter: AgentAdapter
  initialMessages?: AgentMessage[]
  children: React.ReactNode
}) {
  const [messages, setMessages] =
    React.useState<AgentMessage[]>(initialMessages)
  const [isStreaming, setIsStreaming] = React.useState(false)

  const send = React.useCallback(
    async (text: string) => {
      const userMsg: AgentMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      }
      const next = [...messages, userMsg]
      setMessages(next)
      setIsStreaming(true)
      try {
        const reply = await adapter.send(sessionId, next)
        setMessages([...next, ...reply])
      } finally {
        setIsStreaming(false)
      }
    },
    [adapter, messages, sessionId]
  )

  const value = React.useMemo(
    () => ({ sessionId, adapter, messages, send, isStreaming }),
    [sessionId, adapter, messages, send, isStreaming]
  )

  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>
}

export function useAgent() {
  const ctx = React.useContext(AgentContext)
  if (!ctx) throw new Error("useAgent must be used within AgentProvider")
  return ctx
}
