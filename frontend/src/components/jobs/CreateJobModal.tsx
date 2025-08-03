'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { X } from 'lucide-react'
import { Job, Project, Spider } from '@/types'

interface CreateJobModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (job: Partial<Job>) => void
  projects: Project[]
  spiders: Spider[]
}

export default function CreateJobModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  projects, 
  spiders 
}: CreateJobModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    project: '',
    spider: '',
    priority: 5
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const availableSpiders = spiders.filter(spider => 
    !formData.project || spider.project === formData.project
  )

  const handleProjectChange = (projectId: string) => {
    setFormData(prev => ({
      ...prev,
      project: projectId,
      spider: '' // Reset spider when project changes
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    const newErrors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Job name is required'
    }
    
    if (!formData.project) {
      newErrors.project = 'Project selection is required'
    }
    
    if (!formData.spider) {
      newErrors.spider = 'Spider selection is required'
    }
    
    if (formData.priority < 1 || formData.priority > 10) {
      newErrors.priority = 'Priority must be between 1 and 10'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      onSubmit({
        name: formData.name.trim(),
        project: formData.project,
        spider: formData.spider,
        priority: formData.priority
      })
      
      // Reset form
      setFormData({
        name: '',
        project: '',
        spider: '',
        priority: 5
      })
      
      setErrors({})
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Create New Job</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Job Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Job Name *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.name 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
                placeholder="Enter job name"
              />
              {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
              )}
            </div>

            {/* Project Selection */}
            <div>
              <label htmlFor="project" className="block text-sm font-medium text-gray-700 mb-1">
                Project *
              </label>
              <select
                id="project"
                value={formData.project}
                onChange={(e) => handleProjectChange(e.target.value)}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.project 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              >
                <option value="">Select a project</option>
                {projects.filter(p => p.is_active).map(project => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
              {errors.project && (
                <p className="text-red-500 text-xs mt-1">{errors.project}</p>
              )}
            </div>

            {/* Spider Selection */}
            <div>
              <label htmlFor="spider" className="block text-sm font-medium text-gray-700 mb-1">
                Spider *
              </label>
              <select
                id="spider"
                value={formData.spider}
                onChange={(e) => handleChange('spider', e.target.value)}
                disabled={!formData.project}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 disabled:bg-gray-100 ${
                  errors.spider 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              >
                <option value="">
                  {formData.project ? 'Select a spider' : 'Select a project first'}
                </option>
                {availableSpiders.filter(s => s.is_active).map(spider => (
                  <option key={spider.id} value={spider.id}>
                    {spider.name}
                  </option>
                ))}
              </select>
              {errors.spider && (
                <p className="text-red-500 text-xs mt-1">{errors.spider}</p>
              )}
            </div>

            {/* Priority */}
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                Priority (1-10, higher is more important)
              </label>
              <input
                type="number"
                id="priority"
                min="1"
                max="10"
                value={formData.priority}
                onChange={(e) => handleChange('priority', parseInt(e.target.value))}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.priority 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              />
              {errors.priority && (
                <p className="text-red-500 text-xs mt-1">{errors.priority}</p>
              )}
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                Create Job
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}