"use client"

import { Button } from "@workspace/ui/components/button"
import { RiRobot2Line } from "@remixicon/react"

export function AgentSidebarTrigger({ className }: { className?: string }) {
  return (
    <Button
      variant="ghost"
      size="icon-sm"
      className={className}
      onClick={() =>
        window.dispatchEvent(new CustomEvent("toggle-agent-sidebar"))
      }
    >
      <RiRobot2Line />
      <span className="sr-only">Toggle Agent Sidebar</span>
    </Button>
  )
}
