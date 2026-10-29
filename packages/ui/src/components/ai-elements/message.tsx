"use client"

import { cn } from "cn"

export function Message({
  role,
  children,
  className,
}: {
  role: "user" | "assistant"
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn("flex gap-3", role === "user" && "justify-end", className)}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2 text-sm",
          role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        {children}
      </div>
    </div>
  )
}
