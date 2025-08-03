'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { X, Download, Clock, Target, TrendingUp, Calendar } from 'lucide-react'
import { Job } from '@/types'
import { mockSpiders, mockProjects } from '@/lib/mockData'

interface JobDetailsModalProps {
  job: Job
  onClose: () => void
  onUpdate: (job: Job) => void
}

export default function JobDetailsModal({ job, onClose, onUpdate }: JobDetailsModalProps) {
  const spider = mockSpiders.find(s => s.id === job.spider)
  const project = mockProjects.find(p => p.id === job.project)

  const getStatusBadge = (status: string) => {
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
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const formatDuration = (start?: string, end?: string) => {
    if (!start) return 'Not started'
    if (!end && job.status === 'running') {
      const duration = Date.now() - new Date(start).getTime()
      const hours = Math.floor(duration / 3600000)
      const minutes = Math.floor((duration % 3600000) / 60000)
      const seconds = Math.floor((duration % 60000) / 1000)
      return `${hours}h ${minutes}m ${seconds}s (running)`
    }
    if (!end) return 'Not finished'
    
    const duration = new Date(end).getTime() - new Date(start).getTime()
    const hours = Math.floor(duration / 3600000)
    const minutes = Math.floor((duration % 3600000) / 60000)
    const seconds = Math.floor((duration % 60000) / 1000)
    return `${hours}h ${minutes}m ${seconds}s`
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CardTitle className="text-xl">{job.name}</CardTitle>
              {getStatusBadge(job.status)}
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Job Information</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-600">Job ID</label>
                  <p className="text-sm text-gray-900 font-mono">{job.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Project</label>
                  <p className="text-sm text-gray-900">{project?.name || 'Unknown'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Spider</label>
                  <p className="text-sm text-gray-900">{spider?.name || 'Unknown'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Priority</label>
                  <p className="text-sm text-gray-900">{job.priority}</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Timing</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-600">Created</label>
                  <p className="text-sm text-gray-900">{formatDate(job.created_at)}</p>
                </div>
                {job.started_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Started</label>
                    <p className="text-sm text-gray-900">{formatDate(job.started_at)}</p>
                  </div>
                )}
                {job.finished_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Finished</label>
                    <p className="text-sm text-gray-900">{formatDate(job.finished_at)}</p>
                  </div>
                )}
                <div>
                  <label className="text-sm font-medium text-gray-600">Duration</label>
                  <p className="text-sm text-gray-900">{formatDuration(job.started_at, job.finished_at)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Progress */}
          {job.status === 'running' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Progress</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Completion</span>
                  <span className="text-sm font-medium">{job.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Statistics */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Statistics</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <Target className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                <div className="text-lg font-semibold text-gray-900">
                  {job.items_scraped.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Items Scraped</div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <TrendingUp className="h-6 w-6 text-green-500 mx-auto mb-2" />
                <div className="text-lg font-semibold text-gray-900">
                  {job.status === 'done' ? '100' : job.progress}%
                </div>
                <div className="text-sm text-gray-600">Complete</div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <Clock className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                <div className="text-lg font-semibold text-gray-900">
                  {job.priority}
                </div>
                <div className="text-sm text-gray-600">Priority</div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {job.error_message && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-red-600">Error Details</h3>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{job.error_message}</p>
              </div>
            </div>
          )}

          {/* Result File */}
          {job.result_file && job.status === 'done' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Results</h3>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-800">Results Available</p>
                    <p className="text-sm text-green-600">{job.result_file}</p>
                  </div>
                  <Button size="sm" className="bg-green-600 hover:bg-green-700">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Configuration */}
          {spider && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Spider Configuration</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div>
                  <label className="text-sm font-medium text-gray-600">Start URLs</label>
                  <div className="mt-1">
                    {spider.start_urls.map((url, index) => (
                      <p key={index} className="text-sm text-gray-900 font-mono break-all">
                        {url}
                      </p>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Allowed Domains</label>
                  <p className="text-sm text-gray-900">{spider.allowed_domains.join(', ')}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Download Delay</label>
                    <p className="text-sm text-gray-900">
                      {spider.custom_settings.download_delay || 'Default'}s
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Concurrent Requests</label>
                    <p className="text-sm text-gray-900">
                      {spider.custom_settings.concurrent_requests || 'Default'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            {job.result_file && job.status === 'done' && (
              <Button>
                <Download className="h-4 w-4 mr-2" />
                Download Results
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}