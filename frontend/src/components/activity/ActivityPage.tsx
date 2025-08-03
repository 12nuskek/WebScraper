'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { 
  RefreshCw, 
  Filter, 
  Search,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Pause
} from 'lucide-react'

interface ActivityLog {
  id: string
  timestamp: string
  type: 'job' | 'spider' | 'schedule' | 'system' | 'error'
  level: 'info' | 'success' | 'warning' | 'error'
  title: string
  description: string
  source: string
  details?: string
}

// Mock activity data
const mockActivities: ActivityLog[] = [
  {
    id: '1',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    type: 'job',
    level: 'success',
    title: 'Job Completed Successfully',
    description: 'Daily Product Scrape finished with 1,247 items collected',
    source: 'Amazon Product Spider'
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    type: 'spider',
    level: 'info',
    title: 'Spider Started',
    description: 'eBay Price Monitor spider began execution',
    source: 'eBay Price Monitor'
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    type: 'error',
    level: 'error',
    title: 'Request Failed',
    description: 'HTTP 403 Forbidden error encountered',
    source: 'News Spider',
    details: 'URL: https://news.example.com/blocked, Status: 403, Retries: 3'
  },
  {
    id: '4',
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    type: 'schedule',
    level: 'info',
    title: 'Scheduled Job Triggered',
    description: 'Hourly news collection schedule executed',
    source: 'News Collection Schedule'
  },
  {
    id: '5',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    type: 'system',
    level: 'warning',
    title: 'High Memory Usage',
    description: 'System memory usage reached 85%',
    source: 'System Monitor'
  },
  {
    id: '6',
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
    type: 'job',
    level: 'success',
    title: 'Data Export Completed',
    description: 'CSV export of social media data finished',
    source: 'Data Export Service'
  }
]

export default function ActivityPage() {
  const [activities, setActivities] = useState<ActivityLog[]>(mockActivities)
  const [filteredActivities, setFilteredActivities] = useState<ActivityLog[]>(mockActivities)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Auto-refresh simulation
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      // Simulate new activity (in real app, this would be WebSocket or polling)
      const newActivity: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: ['job', 'spider', 'system'][Math.floor(Math.random() * 3)] as any,
        level: ['info', 'success', 'warning'][Math.floor(Math.random() * 3)] as any,
        title: 'New Activity',
        description: 'Simulated real-time activity update',
        source: 'Mock Source'
      }
      setActivities(prev => [newActivity, ...prev])
    }, 30000) // Add new activity every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  // Filter activities
  useEffect(() => {
    let filtered = activities

    if (searchTerm) {
      filtered = filtered.filter(activity =>
        activity.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.source.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(activity => activity.type === filterType)
    }

    if (filterLevel !== 'all') {
      filtered = filtered.filter(activity => activity.level === filterLevel)
    }

    setFilteredActivities(filtered)
  }, [activities, searchTerm, filterType, filterLevel])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMs / 60000)
    
    if (diffMinutes < 1) return 'Just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    
    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    
    return date.toLocaleDateString()
  }

  const getActivityIcon = (type: string, level: string) => {
    if (level === 'error') return <XCircle className="h-5 w-5 text-red-500" />
    if (level === 'warning') return <AlertTriangle className="h-5 w-5 text-yellow-500" />
    if (level === 'success') return <CheckCircle className="h-5 w-5 text-green-500" />
    
    switch (type) {
      case 'job': return <Activity className="h-5 w-5 text-blue-500" />
      case 'spider': return <Activity className="h-5 w-5 text-purple-500" />
      case 'schedule': return <Clock className="h-5 w-5 text-orange-500" />
      default: return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const getLevelBadge = (level: string) => {
    const variants = {
      info: 'bg-blue-100 text-blue-800',
      success: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800'
    }
    
    return (
      <Badge className={variants[level as keyof typeof variants]}>
        {level.charAt(0).toUpperCase() + level.slice(1)}
      </Badge>
    )
  }

  const getTypeBadge = (type: string) => {
    const variants = {
      job: 'bg-blue-100 text-blue-800',
      spider: 'bg-purple-100 text-purple-800',
      schedule: 'bg-orange-100 text-orange-800',
      system: 'bg-gray-100 text-gray-800',
      error: 'bg-red-100 text-red-800'
    }
    
    return (
      <Badge className={variants[type as keyof typeof variants]} variant="outline">
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    )
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-6">
          {/* Page Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Activity</h1>
                <p className="text-gray-600">Real-time system activity and logs</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button
                  variant={autoRefresh ? "default" : "outline"}
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  size="sm"
                >
                  {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                  {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
                </Button>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>

            {/* Search and Filter Bar */}
            <div className="flex items-center space-x-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search activity..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-10 w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Types</option>
                  <option value="job">Jobs</option>
                  <option value="spider">Spiders</option>
                  <option value="schedule">Schedules</option>
                  <option value="system">System</option>
                  <option value="error">Errors</option>
                </select>
                
                <select
                  value={filterLevel}
                  onChange={(e) => setFilterLevel(e.target.value)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Levels</option>
                  <option value="info">Info</option>
                  <option value="success">Success</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>
          </div>

          {/* Activity Stream */}
          <div className="space-y-4">
            {filteredActivities.map((activity) => (
              <div key={activity.id} className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    {getActivityIcon(activity.type, activity.level)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold text-gray-900">{activity.title}</h3>
                        {getLevelBadge(activity.level)}
                        {getTypeBadge(activity.type)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatTime(activity.timestamp)}
                      </div>
                    </div>
                    
                    <p className="text-gray-600 mb-2">{activity.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        Source: <span className="font-medium">{activity.source}</span>
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(activity.timestamp).toLocaleString()}
                      </div>
                    </div>
                    
                    {activity.details && (
                      <div className="mt-3 p-3 bg-gray-50 rounded border text-sm text-gray-600">
                        <strong>Details:</strong> {activity.details}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {filteredActivities.length === 0 && (
              <div className="text-center py-12 bg-white rounded-lg border">
                <Activity className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-900">No activity found</p>
                <p className="text-sm text-gray-600">Try adjusting your filters or check back later</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}