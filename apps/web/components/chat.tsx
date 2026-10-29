"use client"

import * as React from "react"

import { Markdown } from "@workspace/ui/components/markdown"
import { PromptInput } from "@workspace/ui/components/ai-elements/prompt-input"
import { Message, MessageContent } from "@workspace/ui/components/message"
import { Bubble, BubbleContent } from "@workspace/ui/components/bubble"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type Msg = { id: string; role: "user" | "assistant"; content: string }

export function AgentChat() {
  const [messages, setMessages] = React.useState<Msg[]>([])
  const [streaming, setStreaming] = React.useState(false)

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
    const res = await fetch(`${API_URL}/api/v1/chat/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt_input: text, model }),
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
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsg.id ? { ...m, content: m.content + data } : m
            )
          )
        }
      }
    }
    setStreaming(false)
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
      <PromptInput
        onSubmit={(text, model) => handleSend(text, model)}
        disabled={streaming}
      />
    </div>
  )
}
