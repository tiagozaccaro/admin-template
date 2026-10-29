"use client"

import { cn } from "cn"
import { Button } from "@workspace/ui/components/button"
import { PromptInput } from "@workspace/ui/components/ai-elements/prompt-input"
import { Message } from "@workspace/ui/components/message"
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@workspace/ui/components/message-scroller"
import { Bubble, BubbleContent } from "@workspace/ui/components/bubble"

export type ChatMessage = {
  id: string
  role: "user" | "assistant" | "system" | "tool"
  content: string
}

export function Chat({
  messages,
  onSend,
  isStreaming = false,
  className,
}: {
  messages: ChatMessage[]
  onSend: (text: string) => void
  isStreaming?: boolean
  className?: string
}) {
  return (
    <div className={cn("flex h-full flex-col", className)}>
      <MessageScrollerProvider autoScroll>
        <MessageScroller className="min-h-0 flex-1">
          <MessageScrollerViewport>
            <MessageScrollerContent>
              {messages.length === 0 && (
                <div className="text-sm text-muted-foreground">
                  Ask the agent to change your code.
                </div>
              )}
              {messages.map((m) => (
                <MessageScrollerItem
                  key={m.id}
                  messageId={m.id}
                  scrollAnchor={m.role === "user"}
                >
                  <Message align={m.role === "user" ? "end" : "start"}>
                    <Bubble
                      align={m.role === "user" ? "end" : "start"}
                      variant={m.role === "user" ? "muted" : "default"}
                    >
                      <BubbleContent>{m.content}</BubbleContent>
                    </Bubble>
                  </Message>
                </MessageScrollerItem>
              ))}
              {isStreaming && (
                <MessageScrollerItem messageId="streaming">
                  <Message align="start">
                    <Bubble align="start">
                      <BubbleContent>Thinking…</BubbleContent>
                    </Bubble>
                  </Message>
                </MessageScrollerItem>
              )}
            </MessageScrollerContent>
          </MessageScrollerViewport>
          <MessageScrollerButton />
        </MessageScroller>
        <PromptInput onSubmit={onSend} disabled={isStreaming} />
      </MessageScrollerProvider>
    </div>
  )
}
