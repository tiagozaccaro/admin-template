"use client"

import * as React from "react"
import { Markdown } from "@workspace/ui/components/markdown"
import { PromptInput } from "@workspace/ui/components/ai-elements/prompt-input"
import { Message, MessageContent } from "@workspace/ui/components/message"
import { Bubble, BubbleContent } from "@workspace/ui/components/bubble"
import { ApprovalDialog, type ApprovalRequest } from "./approval-dialog"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type Msg = { id: string; role: "user" | "assistant"; content: string }

type AgentChatProps = {
  agentUrl?: string
  agentId?: string
  token?: string
  onApprove?: (request: ApprovalRequest) => void
  onDeny?: (request: ApprovalRequest) => void
}

export function AgentChat({
  agentUrl,
  agentId,
  token,
  onApprove,
  onDeny,
}: AgentChatProps) {
  const [messages, setMessages] = React.useState<Msg[]>([])
  const [streaming, setStreaming] = React.useState(false)
  const [sessionId] = React.useState(() => crypto.randomUUID())
  const [pendingApproval, setPendingApproval] =
    React.useState<ApprovalRequest | null>(null)
  const [approvalError, setApprovalError] = React.useState<string | null>(null)

  // Resolve the chat endpoint: prefer the agent's own daemon URL, fall back
  // to the core API proxy.
  const endpoint = React.useMemo(() => {
    if (agentUrl) {
      return `${agentUrl.replace(/\/$/, "")}/chat/agent`
    }
    const base = agentId
      ? `${API_URL}/api/v1/agents/${agentId}/chat`
      : `${API_URL}/api/v1/chat/agent`
    return base
  }, [agentUrl, agentId])

  async function handleSend(text: string, model: string) {
    const userMsg: Msg = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    }
    const assistantMsg: Msg = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
    }
    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setStreaming(true)
    setApprovalError(null)
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
    const res = await fetch(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify({
        prompt_input: text,
        model,
        session_id: sessionId,
      }),
    })
    if (!res.body) {
      setStreaming(false)
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n\n")
      buffer = lines.pop() ?? ""
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6)
          if (data === "[DONE]") {
            setStreaming(false)
            return
          }
          try {
            const parsed = JSON.parse(data) as {
              delta?: string
              error?: string
              approval_request?: ApprovalRequest
            }
            if (parsed.approval_request) {
              setPendingApproval(parsed.approval_request)
              setStreaming(false)
              return
            }
            if (parsed.delta) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsg.id
                    ? { ...m, content: m.content + parsed.delta }
                    : m
                )
              )
            }
          } catch {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsg.id
                  ? { ...m, content: m.content + data }
                  : m
              )
            )
          }
        }
      }
    }
    setStreaming(false)
  }

  async function handleApprove(request: ApprovalRequest) {
    setPendingApproval(null)
    setStreaming(true)
    setApprovalError(null)
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
    try {
      const res = await fetch(
        `${endpoint.replace(/\/chat\/agent$/, "")}/approve/${request.id}`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ approved: true }),
        }
      )
      if (!res.ok) {
        setApprovalError(`Approval failed (${res.status})`)
      }
    } catch (err) {
      setApprovalError(
        err instanceof Error ? err.message : "Approval request failed"
      )
    } finally {
      setStreaming(false)
    }
  }

  async function handleDeny(request: ApprovalRequest) {
    setPendingApproval(null)
    setStreaming(true)
    setApprovalError(null)
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
    try {
      const res = await fetch(
        `${endpoint.replace(/\/chat\/agent$/, "")}/approve/${request.id}`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ approved: false }),
        }
      )
      if (!res.ok) {
        setApprovalError(`Denial failed (${res.status})`)
      }
    } catch (err) {
      setApprovalError(
        err instanceof Error ? err.message : "Denial request failed"
      )
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="flex h-full flex-col gap-4 p-6">
      <div className="flex-1 space-y-4 overflow-y-auto">
        {messages.map((m) => (
          <Message key={m.id} align={m.role === "user" ? "end" : "start"}>
            <MessageContent>
              <Bubble
                align={m.role === "user" ? "end" : "start"}
                variant={m.role === "user" ? "muted" : "default"}
              >
                <BubbleContent>
                  {m.role === "assistant" ? (
                    <Markdown>{m.content}</Markdown>
                  ) : (
                    m.content
                  )}
                </BubbleContent>
              </Bubble>
            </MessageContent>
          </Message>
        ))}
      </div>
      {approvalError && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          {approvalError}
        </div>
      )}
      <PromptInput
        onSubmit={(text, model) => handleSend(text, model)}
        disabled={streaming}
      />
      <ApprovalDialog
        request={pendingApproval}
        onApprove={handleApprove}
        onDeny={handleDeny}
      />
    </div>
  )
}

export default AgentChat
