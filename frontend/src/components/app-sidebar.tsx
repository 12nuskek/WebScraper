"use client"

import * as React from "react"
import {
  ListTree,
  Network,
  Timer,
  Database,
  ChevronRight,
  Cog,
  Box,
  Activity,
  ShieldCheck,
  User,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "User",
    email: "",
    avatar: "",
  },
  teams: [],
  navMain: [
    {
      title: "Overview",
      url: "/dashboard",
      icon: Activity,
      isActive: true,
      items: [
        { title: "KPI & Charts", url: "/dashboard" },
      ],
    },
    {
      title: "Projects",
      url: "/dashboard/projects",
      icon: Box,
      items: [
        { title: "All Projects", url: "/dashboard/projects" },
      ],
    },
    {
      title: "Spiders",
      url: "/dashboard/spiders",
      icon: ListTree,
      items: [
        { title: "All Spiders", url: "/dashboard/spiders" },
      ],
    },
    {
      title: "Jobs",
      url: "/dashboard/jobs",
      icon: Network,
      items: [
        { title: "All Jobs", url: "/dashboard/jobs" },
      ],
    },
    {
      title: "Requests",
      url: "/dashboard/requests",
      icon: Database,
      items: [
        { title: "Queue", url: "/dashboard/requests" },
      ],
    },
    {
      title: "Responses",
      url: "/dashboard/responses",
      icon: ShieldCheck,
      items: [
        { title: "All Responses", url: "/dashboard/responses" },
      ],
    },
    {
      title: "Schedules",
      url: "/dashboard/schedules",
      icon: Timer,
      items: [
        { title: "All Schedules", url: "/dashboard/schedules" },
      ],
    },
    {
      title: "Proxies",
      url: "/dashboard/proxies",
      icon: Cog,
      items: [
        { title: "Pool", url: "/dashboard/proxies" },
      ],
    },
    {
      title: "Sessions",
      url: "/dashboard/sessions",
      icon: User,
      items: [
        { title: "All Sessions", url: "/dashboard/sessions" },
      ],
    },
  ],
  projects: [],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
