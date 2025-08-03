'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { 
  MoreHorizontal, 
  Play, 
  Pause, 
  Settings, 
  Trash2, 
  Globe,
  Target,
  TrendingUp,
  Clock
} from 'lucide-react'
import { Spider } from '@/types'
import { mockProjects } from '@/lib/mockData'

interface SpiderCardProps {
  spider: Spider
  onUpdate: (spider: Spider) => void
  onDelete: (spiderId: string) => void
  onRun: (spiderId: string) => void
}

export default function SpiderCard({ spider, onUpdate, onDelete, onRun }: SpiderCardProps) {
  const [showActions, setShowActions] = useState(false)

  const project = mockProjects.find(p => p.id === spider.project)

  const handleToggleStatus = () => {
    onUpdate({
      ...spider,
      is_active: !spider.is_active,
      updated_at: new Date().toISOString()
    })
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this spider? This action cannot be undone.')) {
      onDelete(spider.id)
    }
  }

  const handleRun = () => {
    onRun(spider.id)
    setShowActions(false)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 95) return 'text-green-600'
    if (rate >= 80) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <Card className="relative hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold text-gray-900 truncate">
              {spider.name}
            </CardTitle>
            <div className="flex items-center mt-2 space-x-2">
              <Badge variant={spider.is_active ? 'default' : 'secondary'}>
                {spider.is_active ? 'Active' : 'Inactive'}
              </Badge>
              {project && (
                <Badge variant="outline" className="text-xs">
                  {project.name}
                </Badge>
              )}
            </div>
          </div>
          
          <div className="relative">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setShowActions(!showActions)}
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
            
            {showActions && (
              <div className="absolute right-0 top-8 bg-white border rounded-md shadow-lg z-10 min-w-[120px]">
                <button
                  onClick={handleRun}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center text-green-600"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Run Now
                </button>
                <button
                  onClick={handleToggleStatus}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  {spider.is_active ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Disable
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Enable
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowActions(false)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Configure
                </button>
                <button
                  onClick={handleDelete}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 text-red-600 flex items-center"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
        
        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
          {spider.description}
        </p>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* URLs and Domains */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-xs text-gray-600">
            <Globe className="h-3 w-3 mr-1" />
            <span className="font-medium">Start URLs:</span>
          </div>
          <div className="pl-4">
            {spider.start_urls.slice(0, 2).map((url, index) => (
              <div key={index} className="text-xs text-gray-500 truncate">
                {url}
              </div>
            ))}
            {spider.start_urls.length > 2 && (
              <div className="text-xs text-gray-400">
                +{spider.start_urls.length - 2} more
              </div>
            )}
          </div>
          
          <div className="flex items-center text-xs text-gray-600 mt-2">
            <Target className="h-3 w-3 mr-1" />
            <span className="font-medium">Domains:</span>
            <span className="ml-1 text-gray-500">
              {spider.allowed_domains.join(', ')}
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className={`h-4 w-4 ${getSuccessRateColor(spider.success_rate)}`} />
            </div>
            <div className={`text-lg font-semibold ${getSuccessRateColor(spider.success_rate)}`}>
              {spider.success_rate}%
            </div>
            <div className="text-xs text-gray-500">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Clock className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {spider.total_requests.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">Total Requests</div>
          </div>
        </div>

        {/* Settings Preview */}
        <div className="bg-gray-50 rounded p-2 mb-4">
          <div className="text-xs text-gray-600 mb-1">Configuration:</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500">Delay:</span>
              <span className="ml-1 font-medium">
                {spider.custom_settings.download_delay || 'None'}s
              </span>
            </div>
            <div>
              <span className="text-gray-500">Concurrent:</span>
              <span className="ml-1 font-medium">
                {spider.custom_settings.concurrent_requests || 'Default'}
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3">
          <span>Created {formatDate(spider.created_at)}</span>
          <span>Updated {formatDate(spider.updated_at)}</span>
        </div>
      </CardContent>
      
      {/* Click outside handler */}
      {showActions && (
        <div 
          className="fixed inset-0 z-5" 
          onClick={() => setShowActions(false)}
        />
      )}
    </Card>
  )
}