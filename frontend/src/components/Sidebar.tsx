'use client'

import { 
  BarChart3, 
  Settings, 
  Users, 
  Globe, 
  Database, 
  Calendar,
  Activity,
  Home,
  FolderOpen
} from "lucide-react"
import { cn } from "@/lib/utils"
import { usePathname, useRouter } from "next/navigation"

interface SidebarProps {
  className?: string
}

const navigationItems = [
  { name: 'Dashboard', icon: Home, href: '/' },
  { name: 'Projects', icon: FolderOpen, href: '/projects' },
  { name: 'Spiders', icon: Globe, href: '/spiders' },
  { name: 'Jobs', icon: Activity, href: '/jobs' },
  { name: 'Data', icon: Database, href: '/data' },
  { name: 'Analytics', icon: BarChart3, href: '/analytics' },
  { name: 'Schedule', icon: Calendar, href: '/schedule' },
  { name: 'Activity', icon: Activity, href: '/activity' },
  { name: 'Settings', icon: Settings, href: '/settings' },
]

export default function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  const handleNavigation = (href: string) => {
    router.push(href)
  }

  return (
    <div className={cn("flex h-full w-64 flex-col bg-gray-900", className)}>
      <div className="flex h-16 items-center justify-center border-b border-gray-800">
        <h1 className="text-xl font-bold text-white">WebScraper</h1>
      </div>
      
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <button
              key={item.name}
              onClick={() => handleNavigation(item.href)}
              className={cn(
                "group flex w-full items-center rounded-md px-2 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-300 hover:bg-gray-700 hover:text-white"
              )}
            >
              <Icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-white" : "text-gray-400 group-hover:text-white"
                )}
              />
              {item.name}
            </button>
          )
        })}
      </nav>
    </div>
  )
}