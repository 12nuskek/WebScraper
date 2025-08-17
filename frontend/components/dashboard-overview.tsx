import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  TrendingUp,
  Database,
  Target,
  FolderOpen,
  Bot,
  CheckCircle,
  AlertTriangle,
  Plus,
  ArrowRight,
  Clock,
  Activity,
  Zap,
  BarChart3,
  Bell,
} from "lucide-react"

export function DashboardOverview() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard Overview</h1>
        <p className="text-sm text-muted-foreground">Last updated: Now</p>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Quick Stats</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Active Projects"
            value="8"
            trend="+2 this week"
            trendUp={true}
            icon={FolderOpen}
            iconColor="text-blue-600"
          />
          <StatsCard
            title="Running Spiders"
            value="23"
            trend="All healthy"
            trendUp={true}
            icon={Bot}
            iconColor="text-green-600"
            badge="Healthy"
          />
          <StatsCard
            title="Data Points"
            value="2.4M today"
            trend="+15% vs avg"
            trendUp={true}
            icon={Database}
            iconColor="text-purple-600"
          />
          <StatsCard
            title="Success Rate"
            value="94.7%"
            trend="Target 95%"
            trendUp={false}
            icon={Target}
            iconColor="text-orange-600"
          />
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Recent Activity</h2>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Live Activity Feed
            </CardTitle>
            <Button variant="ghost" size="sm" className="text-sm">
              View All
              <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            <ActivityItem
              time="2 min ago"
              message="LEGO Spider completed batch (1,247 products)"
              type="success"
              icon={CheckCircle}
            />
            <ActivityItem
              time="5 min ago"
              message="BigW pricing data updated successfully"
              type="success"
              icon={Database}
            />
            <ActivityItem time="8 min ago" message='New project "Wine Analysis" created' type="info" icon={Plus} />
            <ActivityItem
              time="12 min ago"
              message="Alert: Target spider hit rate limit"
              type="warning"
              icon={AlertTriangle}
            />
            <ActivityItem
              time="15 min ago"
              message="Data quality check passed (98.7% accuracy)"
              type="success"
              icon={CheckCircle}
            />
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Project
          </Button>
          <Button variant="outline" className="gap-2 bg-transparent">
            <Plus className="h-4 w-4" />
            Create Spider
          </Button>
          <Button variant="outline" className="gap-2 bg-transparent">
            <BarChart3 className="h-4 w-4" />
            View Analytics
          </Button>
          <Button variant="outline" className="gap-2 bg-transparent">
            <Bell className="h-4 w-4" />
            Alerts
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Active Spiders Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <SpiderCard name="LEGO Official" status="running" rate="2.3k/hr" actionLabel="Manage" />
          <SpiderCard name="BigW Scraper" status="running" rate="1.8k/hr" actionLabel="Manage" />
          <SpiderCard name="Target Monitor" status="rate-limited" rate="Retrying in 5m" actionLabel="Fix" />
          <SpiderCard name="Reddit" status="running" rate="247/hr" actionLabel="View" />
        </div>
      </div>
    </div>
  )
}

interface StatsCardProps {
  title: string
  value: string
  trend: string
  trendUp: boolean
  icon: React.ComponentType<{ className?: string }>
  iconColor: string
  badge?: string
}

function StatsCard({ title, value, trend, trendUp, icon: Icon, iconColor, badge }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${iconColor}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center gap-2 mt-1">
          {trendUp && <TrendingUp className="h-3 w-3 text-green-600" />}
          <p className={`text-xs ${trendUp ? "text-green-600" : "text-muted-foreground"}`}>{trend}</p>
          {badge && (
            <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
              {badge}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface ActivityItemProps {
  time: string
  message: string
  type: "success" | "warning" | "info"
  icon: React.ComponentType<{ className?: string }>
}

function ActivityItem({ time, message, type, icon: Icon }: ActivityItemProps) {
  const getTypeStyles = () => {
    switch (type) {
      case "success":
        return "text-green-600 bg-green-50"
      case "warning":
        return "text-orange-600 bg-orange-50"
      case "info":
        return "text-blue-600 bg-blue-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  return (
    <div className="flex items-start gap-3 py-2">
      <div className={`p-1.5 rounded-full ${getTypeStyles()}`}>
        <Icon className="h-3 w-3" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{message}</p>
        <p className="text-xs text-muted-foreground">{time}</p>
      </div>
    </div>
  )
}

interface SpiderCardProps {
  name: string
  status: "running" | "rate-limited" | "stopped"
  rate: string
  actionLabel: string
}

function SpiderCard({ name, status, rate, actionLabel }: SpiderCardProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "running":
        return {
          badge: "Running",
          badgeVariant: "default" as const,
          badgeClass: "bg-green-100 text-green-800",
          icon: Activity,
          iconClass: "text-green-600",
        }
      case "rate-limited":
        return {
          badge: "Rate Limited",
          badgeVariant: "secondary" as const,
          badgeClass: "bg-yellow-100 text-yellow-800",
          icon: AlertTriangle,
          iconClass: "text-yellow-600",
        }
      case "stopped":
        return {
          badge: "Stopped",
          badgeVariant: "destructive" as const,
          badgeClass: "bg-red-100 text-red-800",
          icon: Bot,
          iconClass: "text-red-600",
        }
      default:
        return {
          badge: "Unknown",
          badgeVariant: "secondary" as const,
          badgeClass: "bg-gray-100 text-gray-800",
          icon: Bot,
          iconClass: "text-gray-600",
        }
    }
  }

  const statusConfig = getStatusConfig()

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{name}</CardTitle>
        <statusConfig.icon className={`h-4 w-4 ${statusConfig.iconClass}`} />
      </CardHeader>
      <CardContent className="space-y-3">
        <Badge className={statusConfig.badgeClass}>{statusConfig.badge}</Badge>
        <div className="flex items-center gap-1">
          <Zap className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{rate}</span>
        </div>
        <Button variant="outline" size="sm" className="w-full bg-transparent">
          {actionLabel}
          <ArrowRight className="h-3 w-3 ml-1" />
        </Button>
      </CardContent>
    </Card>
  )
}
