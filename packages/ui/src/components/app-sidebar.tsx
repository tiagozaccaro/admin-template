"use client"

import * as React from "react"

import { NavDocuments } from "@workspace/ui/components/nav-documents"
import { NavMain } from "@workspace/ui/components/nav-main"
import { NavSecondary } from "@workspace/ui/components/nav-secondary"
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
import {
  RiDashboardLine,
  RiBarChartLine,
  RiGroupLine,
  RiSettingsLine,
  RiFileChartLine,
  RiFileTextLine,
  RiQuestionLine,
  RiLogoutBoxLine,
  RiCommandLine,
} from "@remixicon/react"

const data = {
  user: {
    name: "Admin User",
    email: "user@example.com",
    avatar: "/placeholder.svg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "#",
      icon: <RiDashboardLine />,
    },
    {
      title: "Analytics",
      url: "#",
      icon: <RiBarChartLine />,
    },
    {
      title: "Users",
      url: "#",
      icon: <RiGroupLine />,
    },
    {
      title: "Settings",
      url: "#",
      icon: <RiSettingsLine />,
    },
  ],
  documents: [
    {
      name: "Reports",
      url: "#",
      icon: <RiFileChartLine />,
    },
    {
      name: "Activity log",
      url: "#",
      icon: <RiFileTextLine />,
    },
  ],
  navSecondary: [
    {
      title: "Help",
      url: "#",
      icon: <RiQuestionLine />,
    },
    {
      title: "Sign out",
      url: "#",
      icon: <RiLogoutBoxLine />,
    },
  ],
}
export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
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
        <NavDocuments items={data.documents} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
