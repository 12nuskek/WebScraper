'use client'

import Sidebar from "@/components/Sidebar"
import Header from "@/components/Header"
import StatCard from "@/components/dashboard/StatCard"
import RecentActivity from "@/components/dashboard/RecentActivity"
import ProjectOverview from "@/components/dashboard/ProjectOverview"
import ChartPlaceholder from "@/components/dashboard/ChartPlaceholder"
import { 
  Globe, 
  Database, 
  Activity, 
  Clock,
  TrendingUp,
  AlertCircle
} from "lucide-react"

export default function Dashboard() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Dashboard Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <StatCard
              title="Active Spiders"
              value={24}
              change="+2 from last week"
              changeType="positive"
              icon={Globe}
            />
            <StatCard
              title="Data Points Collected"
              value="1,247,890"
              change="+15.3% from last month"
              changeType="positive"
              icon={Database}
            />
            <StatCard
              title="Success Rate"
              value="98.2%"
              change="+0.5% from yesterday"
              changeType="positive"
              icon={TrendingUp}
            />
            <StatCard
              title="Failed Requests"
              value={156}
              change="-12% from last week"
              changeType="positive"
              icon={AlertCircle}
            />
          </div>
          
          {/* Charts and Activity Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-2">
              <ChartPlaceholder 
                title="Scraping Activity Over Time"
                description="Monitor your scraping performance and trends"
                height={350}
              />
            </div>
            <div>
              <RecentActivity />
            </div>
          </div>
          
          {/* Projects and Performance Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProjectOverview />
            <ChartPlaceholder 
              title="Performance Metrics"
              description="Response times and success rates by domain"
              height={400}
            />
          </div>
        </main>
      </div>
    </div>
  )
}