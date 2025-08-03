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
  Calendar,
  Activity
} from 'lucide-react'
import { Project } from '@/types'

interface ProjectCardProps {
  project: Project
  onUpdate: (project: Project) => void
  onDelete: (projectId: string) => void
}

export default function ProjectCard({ project, onUpdate, onDelete }: ProjectCardProps) {
  const [showActions, setShowActions] = useState(false)

  const handleToggleStatus = () => {
    onUpdate({
      ...project,
      is_active: !project.is_active,
      updated_at: new Date().toISOString()
    })
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      onDelete(project.id)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Card className="relative hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold text-gray-900 truncate">
              {project.name}
            </CardTitle>
            <div className="flex items-center mt-2 space-x-2">
              <Badge variant={project.is_active ? 'default' : 'secondary'}>
                {project.is_active ? 'Active' : 'Inactive'}
              </Badge>
              {project.last_run && (
                <span className="text-xs text-gray-500">
                  Last run: {project.last_run}
                </span>
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
                  onClick={handleToggleStatus}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  {project.is_active ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Resume
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowActions(false)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
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
          {project.description}
        </p>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Globe className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">{project.spider_count}</div>
            <div className="text-xs text-gray-500">Spiders</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Activity className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">{project.job_count}</div>
            <div className="text-xs text-gray-500">Jobs</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Calendar className="h-4 w-4 text-purple-500" />
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {project.settings.max_concurrent_requests || 5}
            </div>
            <div className="text-xs text-gray-500">Max Req</div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3">
          <span>Created {formatDate(project.created_at)}</span>
          <span>Updated {formatDate(project.updated_at)}</span>
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