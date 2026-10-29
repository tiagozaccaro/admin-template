"use client"

import * as React from "react"

import { NavMain } from "@workspace/ui/components/nav-main"
import { NavUser } from "@workspace/ui/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@workspace/ui/components/sidebar"
import { RiDashboardLine, RiCommandLine, RiRobot2Line } from "@remixicon/react"

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: <RiDashboardLine />,
    },
    {
      title: "Chat",
      url: "/chat",
      icon: <RiRobot2Line />,
    },
  ],
}
export function AppSidebar({
  user,
  onSignOut,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  user: { name: string; email: string; avatar: string }
  onSignOut?: () => void
}) {
  function handleSignOut() {
    if (onSignOut) {
      onSignOut()
      return
    }
    if (typeof window !== "undefined") {
      window.location.href = "/auth/logout"
    }
  }

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              className="data-[slot=sidebar-menu-button]:p-1.5!"
              render={<a href="#" />}
            >
              <RiCommandLine className="size-5!" />
              <span className="text-base font-semibold">Admin Template</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} onSignOut={handleSignOut} />
      </SidebarFooter>
    </Sidebar>
  )
}
