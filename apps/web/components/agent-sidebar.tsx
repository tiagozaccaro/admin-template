"use client"

import { useEffect, useState } from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from "@workspace/ui/components/sidebar"
import { RiRobot2Line } from "@remixicon/react"
import { AgentTabs } from "@workspace/ui/components/ai-elements/agent-tabs"
import { HttpAdapter } from "@workspace/ui/lib/http-adapter"

const adapter = new HttpAdapter("/api/v1/chat")

export function AgentSidebar() {
  const [open, setOpen] = useState(true)
  useEffect(() => {
    const handler = () => setOpen((v) => !v)
    window.addEventListener("toggle-agent-sidebar", handler)
    return () => window.removeEventListener("toggle-agent-sidebar", handler)
  }, [])
  if (!open) return null
  return (
    <>
      <Sidebar side="right" collapsible="icon">
        <SidebarHeader className="p-1.5">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton className="data-[slot=sidebar-menu-button]:p-1.5!">
                <RiRobot2Line className="size-5!" />
                <span className="text-base font-semibold">Agent</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent className="p-2">
          <AgentTabs adapter={adapter} />
        </SidebarContent>
      </Sidebar>
    </>
  )
}
