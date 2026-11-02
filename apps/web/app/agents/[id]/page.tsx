import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { ChatPageClient } from "./chat-page-client"

export const metadata: Metadata = {
  title: "Agent chat | Admin Template",
  description: "Chat with a standalone machine admin agent",
}

export default async function AgentChatPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  if (!id) {
    redirect("/agents")
  }
  return <ChatPageClient agentId={id} />
}
