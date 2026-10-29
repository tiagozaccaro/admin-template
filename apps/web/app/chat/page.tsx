"use client"

import { AgentChat } from "@/components/chat"

export default function ChatPage() {
  return (
    <div className="flex h-full min-h-0 flex-col gap-4 px-4 py-4 md:gap-6 md:py-6 lg:px-6">
      <AgentChat />
    </div>
  )
}
