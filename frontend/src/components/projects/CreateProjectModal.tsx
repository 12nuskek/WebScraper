'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { X } from 'lucide-react'
import { Project } from '@/types'

interface CreateProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (project: Partial<Project>) => void
}

export default function CreateProjectModal({ isOpen, onClose, onSubmit }: CreateProjectModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    max_concurrent_requests: 5,
    delay: 1,
    is_active: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    const newErrors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Project description is required'
    }
    
    if (formData.max_concurrent_requests < 1 || formData.max_concurrent_requests > 50) {
      newErrors.max_concurrent_requests = 'Max concurrent requests must be between 1 and 50'
    }
    
    if (formData.delay < 0 || formData.delay > 60) {
      newErrors.delay = 'Delay must be between 0 and 60 seconds'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      onSubmit({
        name: formData.name.trim(),
        description: formData.description.trim(),
        is_active: formData.is_active,
        settings: {
          max_concurrent_requests: formData.max_concurrent_requests,
          delay: formData.delay
        }
      })
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        max_concurrent_requests: 5,
        delay: 1,
        is_active: true
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
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Create New Project</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Project Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Project Name *
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
                placeholder="Enter project name"
              />
              {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 resize-none ${
                  errors.description 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
                placeholder="Describe what this project will scrape"
              />
              {errors.description && (
                <p className="text-red-500 text-xs mt-1">{errors.description}</p>
              )}
            </div>

            {/* Max Concurrent Requests */}
            <div>
              <label htmlFor="max_requests" className="block text-sm font-medium text-gray-700 mb-1">
                Max Concurrent Requests
              </label>
              <input
                type="number"
                id="max_requests"
                min="1"
                max="50"
                value={formData.max_concurrent_requests}
                onChange={(e) => handleChange('max_concurrent_requests', parseInt(e.target.value))}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.max_concurrent_requests 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              />
              {errors.max_concurrent_requests && (
                <p className="text-red-500 text-xs mt-1">{errors.max_concurrent_requests}</p>
              )}
            </div>

            {/* Delay */}
            <div>
              <label htmlFor="delay" className="block text-sm font-medium text-gray-700 mb-1">
                Request Delay (seconds)
              </label>
              <input
                type="number"
                id="delay"
                min="0"
                max="60"
                step="0.1"
                value={formData.delay}
                onChange={(e) => handleChange('delay', parseFloat(e.target.value))}
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.delay 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              />
              {errors.delay && (
                <p className="text-red-500 text-xs mt-1">{errors.delay}</p>
              )}
            </div>

            {/* Active Status */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => handleChange('is_active', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                Start project as active
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                Create Project
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}