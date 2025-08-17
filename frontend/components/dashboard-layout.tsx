"use client"

import type React from "react"
import { Search, ChevronDown, User, Home, BarChart3, Settings, Activity, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ProjectCreationForm } from "./project-creation-form"
import { SpiderCreationForm } from "./spider-creation-form"
import { CreateModalProvider, useCreateModal } from "./create-modal-context"
import Link from "next/link"
import { usePathname } from "next/navigation"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <CreateModalProvider>
      <DashboardLayoutContent>{children}</DashboardLayoutContent>
    </CreateModalProvider>
  )
}

function DashboardLayoutContent({ children }: DashboardLayoutProps) {
  const {
    isCreateModalOpen,
    setIsCreateModalOpen,
    showProjectForm,
    setShowProjectForm,
    showSpiderForm,
    setShowSpiderForm,
  } = useCreateModal()
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="flex h-16 items-center px-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Home className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">ScrapeMaster</span>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search projects, spiders..." className="w-80 pl-10" />
            </div>
          </div>

          <div className="ml-auto flex items-center gap-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2 bg-transparent">
                  Workspace: Market Research
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem>Market Research</DropdownMenuItem>
                <DropdownMenuItem>E-commerce Analysis</DropdownMenuItem>
                <DropdownMenuItem>Price Monitoring</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 border-r bg-card">
          <nav className="p-4 space-y-2">
            <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
              <DialogTrigger asChild>
                <Button className="w-full justify-start gap-3 bg-primary text-primary-foreground hover:bg-primary/90">
                  <Plus className="h-4 w-4" />
                  Quick Create
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
                {!showProjectForm && !showSpiderForm ? (
                  <>
                    <DialogHeader>
                      <DialogTitle>Create New</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-3 py-4">
                      <Button
                        variant="outline"
                        className="justify-start gap-3 h-12 bg-transparent"
                        onClick={() => setShowProjectForm(true)}
                      >
                        <Home className="h-5 w-5" />
                        <div className="text-left">
                          <div className="font-medium">Create Project</div>
                          <div className="text-sm text-muted-foreground">Start a new scraping project</div>
                        </div>
                      </Button>
                      <Button
                        variant="outline"
                        className="justify-start gap-3 h-12 bg-transparent"
                        onClick={() => setShowSpiderForm(true)}
                      >
                        <Activity className="h-5 w-5" />
                        <div className="text-left">
                          <div className="font-medium">Create Spider</div>
                          <div className="text-sm text-muted-foreground">Build a new web scraper</div>
                        </div>
                      </Button>
                    </div>
                  </>
                ) : showProjectForm ? (
                  <ProjectCreationForm
                    onClose={() => {
                      setShowProjectForm(false)
                      setIsCreateModalOpen(false)
                    }}
                  />
                ) : (
                  <SpiderCreationForm
                    onClose={() => {
                      setShowSpiderForm(false)
                      setIsCreateModalOpen(false)
                    }}
                  />
                )}
              </DialogContent>
            </Dialog>

            <NavItem icon={BarChart3} label="Dashboard" href="/" active={pathname === "/"} />
            <NavItem icon={Home} label="Projects" href="/projects" active={pathname === "/projects"} />
            <NavItem icon={Activity} label="Spiders" href="/spiders" active={pathname === "/spiders"} />
            <NavItem icon={Settings} label="Settings" href="/settings" active={pathname === "/settings"} />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}

interface NavItemProps {
  icon: React.ComponentType<{ className?: string }>
  label: string
  href: string
  active?: boolean
  badge?: string
}

function NavItem({ icon: Icon, label, href, active, badge }: NavItemProps) {
  return (
    <Link href={href}>
      <Button variant={active ? "secondary" : "ghost"} className="w-full justify-start gap-3">
        <Icon className="h-4 w-4" />
        {label}
        {badge && (
          <Badge variant="destructive" className="ml-auto">
            {badge}
          </Badge>
        )}
      </Button>
    </Link>
  )
}
