"use client"

import { Chat } from "@workspace/ui/components/ai-elements/chat"
import { useAgent } from "@workspace/ui/components/ai-elements/agent-provider"

export function AgentChat() {
  const { messages, send, isStreaming } = useAgent()
  return <Chat messages={messages} onSend={send} isStreaming={isStreaming} />
}
