import type { AgentAdapter, AgentMessage } from "./agent-adapter.js"

export class HttpAdapter implements AgentAdapter {
  constructor(private url: string) {}
  async send(
    _sessionId: string,
    messages: AgentMessage[]
  ): Promise<AgentMessage[]> {
    const res = await fetch(this.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    })
    const data = await res.json()
    return [{ id: crypto.randomUUID(), role: "assistant", content: data.reply }]
  }
}
