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
  Clock,
  Calendar,
  Target,
  RotateCcw
} from 'lucide-react'
import { Schedule } from '@/types'
import { mockSpiders } from '@/lib/mockData'

interface ScheduleCardProps {
  schedule: Schedule
  onUpdate: (schedule: Schedule) => void
  onDelete: (scheduleId: string) => void
  onToggle: (scheduleId: string) => void
}

export default function ScheduleCard({ schedule, onUpdate, onDelete, onToggle }: ScheduleCardProps) {
  const [showActions, setShowActions] = useState(false)

  const spider = mockSpiders.find(s => s.id === schedule.spider)

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this schedule? This action cannot be undone.')) {
      onDelete(schedule.id)
    }
    setShowActions(false)
  }

  const handleToggle = () => {
    onToggle(schedule.id)
    setShowActions(false)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = date.getTime() - now.getTime()
    const diffHours = Math.ceil(diffMs / (1000 * 60 * 60))
    
    if (diffHours < 1) {
      const diffMinutes = Math.ceil(diffMs / (1000 * 60))
      return diffMinutes <= 0 ? 'Now' : `in ${diffMinutes}m`
    }
    if (diffHours < 24) {
      return `in ${diffHours}h`
    }
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatLastRun = (dateString?: string) => {
    if (!dateString) return 'Never'
    
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    
    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return diffMinutes === 0 ? 'Just now' : `${diffMinutes}m ago`
    }
    if (diffHours < 24) {
      return `${diffHours}h ago`
    }
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  const getCronDescription = (cronExpression: string) => {
    // Simple cron expression descriptions
    const descriptions: Record<string, string> = {
      '0 * * * *': 'Every hour',
      '0 9 * * *': 'Daily at 9:00 AM',
      '0 0 * * 0': 'Weekly on Sunday',
      '0 0 1 * *': 'Monthly on 1st',
      '*/5 * * * *': 'Every 5 minutes',
      '*/15 * * * *': 'Every 15 minutes',
      '0 */6 * * *': 'Every 6 hours'
    }
    
    return descriptions[cronExpression] || cronExpression
  }

  return (
    <Card className="relative hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold text-gray-900 truncate">
              {schedule.name}
            </CardTitle>
            <div className="flex items-center mt-2 space-x-2">
              <Badge variant={schedule.is_enabled ? 'default' : 'secondary'}>
                {schedule.is_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
              {spider && (
                <Badge variant="outline" className="text-xs">
                  {spider.name}
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
                  onClick={handleToggle}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  {schedule.is_enabled ? (
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
                  onClick={() => console.log('Run now:', schedule.id)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center text-green-600"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Run Now
                </button>
                <button
                  onClick={() => setShowActions(false)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Edit
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
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Cron Expression */}
        <div className="bg-gray-50 rounded p-3 mb-4">
          <div className="flex items-center text-xs text-gray-600 mb-1">
            <Clock className="h-3 w-3 mr-1" />
            <span className="font-medium">Schedule:</span>
          </div>
          <div className="text-sm text-gray-900 font-medium">
            {getCronDescription(schedule.cron_expression)}
          </div>
          <div className="text-xs text-gray-500 font-mono mt-1">
            {schedule.cron_expression}
          </div>
        </div>

        {/* Next/Last Run Info */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="flex items-center text-xs text-gray-600 mb-1">
              <Calendar className="h-3 w-3 mr-1" />
              <span className="font-medium">Next Run:</span>
            </div>
            <div className={`text-sm font-medium ${
              schedule.is_enabled ? 'text-blue-600' : 'text-gray-400'
            }`}>
              {schedule.is_enabled ? formatDate(schedule.next_run) : 'Disabled'}
            </div>
          </div>
          
          <div>
            <div className="flex items-center text-xs text-gray-600 mb-1">
              <Target className="h-3 w-3 mr-1" />
              <span className="font-medium">Last Run:</span>
            </div>
            <div className="text-sm text-gray-900">
              {formatLastRun(schedule.last_run)}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {schedule.run_count}
            </div>
            <div className="text-xs text-gray-500">Total Runs</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {schedule.is_enabled ? (
                <span className="text-green-600">Active</span>
              ) : (
                <span className="text-gray-400">Inactive</span>
              )}
            </div>
            <div className="text-xs text-gray-500">Status</div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3">
          <span>Created {new Date(schedule.created_at).toLocaleDateString()}</span>
          <span>Updated {new Date(schedule.updated_at).toLocaleDateString()}</span>
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