export type AgentMessage = {
  id: string
  role: "user" | "assistant" | "system" | "tool"
  content: string
}

export interface AgentAdapter {
  send(sessionId: string, messages: AgentMessage[]): Promise<AgentMessage[]>
}
