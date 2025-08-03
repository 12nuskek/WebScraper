'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { 
  MoreHorizontal, 
  Play, 
  Pause, 
  RotateCcw,
  Trash2, 
  Eye,
  Download,
  Clock,
  Target,
  TrendingUp
} from 'lucide-react'
import { Job } from '@/types'
import { mockSpiders, mockProjects } from '@/lib/mockData'

interface JobCardProps {
  job: Job
  onUpdate: (job: Job) => void
  onDelete: (jobId: string) => void
  onCancel: (jobId: string) => void
  onRetry: (jobId: string) => void
  onViewDetails: (job: Job) => void
}

export default function JobCard({ 
  job, 
  onUpdate, 
  onDelete, 
  onCancel, 
  onRetry, 
  onViewDetails 
}: JobCardProps) {
  const [showActions, setShowActions] = useState(false)

  const spider = mockSpiders.find(s => s.id === job.spider)
  const project = mockProjects.find(p => p.id === job.project)

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
      onDelete(job.id)
    }
    setShowActions(false)
  }

  const handleCancel = () => {
    if (confirm('Are you sure you want to cancel this job?')) {
      onCancel(job.id)
    }
    setShowActions(false)
  }

  const handleRetry = () => {
    onRetry(job.id)
    setShowActions(false)
  }

  const handleViewDetails = () => {
    onViewDetails(job)
    setShowActions(false)
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      queued: 'secondary',
      running: 'default',
      done: 'default',
      failed: 'destructive',
      cancelled: 'outline'
    } as const
    
    const colors = {
      queued: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      done: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    }

    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (start?: string, end?: string) => {
    if (!start) return 'Not started'
    if (!end && job.status === 'running') {
      const duration = Date.now() - new Date(start).getTime()
      const minutes = Math.floor(duration / 60000)
      return `${minutes}m (running)`
    }
    if (!end) return 'Not finished'
    
    const duration = new Date(end).getTime() - new Date(start).getTime()
    const minutes = Math.floor(duration / 60000)
    const seconds = Math.floor((duration % 60000) / 1000)
    return `${minutes}m ${seconds}s`
  }

  return (
    <Card className="relative hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {job.name}
              </h3>
              {getStatusBadge(job.status)}
              <Badge variant="outline" className="text-xs">
                Priority: {job.priority}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
              <span>Spider: <span className="font-medium">{spider?.name || 'Unknown'}</span></span>
              <span>Project: <span className="font-medium">{project?.name || 'Unknown'}</span></span>
            </div>
            
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>Created: {formatDate(job.created_at)}</span>
              {job.started_at && (
                <span>Started: {formatDate(job.started_at)}</span>
              )}
              <span>Duration: {formatDuration(job.started_at, job.finished_at)}</span>
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
              <div className="absolute right-0 top-8 bg-white border rounded-md shadow-lg z-10 min-w-[140px]">
                <button
                  onClick={handleViewDetails}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </button>
                
                {job.status === 'failed' && (
                  <button
                    onClick={handleRetry}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center text-blue-600"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Retry
                  </button>
                )}
                
                {(job.status === 'queued' || job.status === 'running') && (
                  <button
                    onClick={handleCancel}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center text-orange-600"
                  >
                    <Pause className="h-4 w-4 mr-2" />
                    Cancel
                  </button>
                )}
                
                {job.result_file && job.status === 'done' && (
                  <button
                    onClick={() => console.log('Download:', job.result_file)}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center text-green-600"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </button>
                )}
                
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

        {/* Progress Bar */}
        {job.status === 'running' && (
          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-600">Progress</span>
              <span className="font-medium">{job.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${job.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {job.error_message && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="text-sm text-red-800">
              <strong>Error:</strong> {job.error_message}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Target className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {job.items_scraped.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">Items Scraped</div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Clock className="h-4 w-4 text-purple-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {job.priority}
            </div>
            <div className="text-xs text-gray-500">Priority</div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {job.status === 'done' ? '100' : job.progress}%
            </div>
            <div className="text-xs text-gray-500">Complete</div>
          </div>
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