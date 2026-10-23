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
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: <RiDashboardLine />,
    },
    {
      title: "Items",
      url: "/items",
      icon: <RiFileTextLine />,
    },
    {
      title: "Account",
      url: "/account",
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
        <NavDocuments items={data.documents} />
        <NavSecondary
          items={data.navSecondary}
          className="mt-auto"
          onItemClick={(item) => {
            if (item.title === "Sign out" || item.title === "Log out") {
              handleSignOut()
            }
          }}
        />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} onSignOut={handleSignOut} />
      </SidebarFooter>
    </Sidebar>
  )
}
