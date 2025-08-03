'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { X, Plus, Trash2 } from 'lucide-react'
import { Spider, Project } from '@/types'

interface CreateSpiderModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (spider: Partial<Spider>) => void
  projects: Project[]
}

export default function CreateSpiderModal({ isOpen, onClose, onSubmit, projects }: CreateSpiderModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    project: '',
    start_urls: [''],
    allowed_domains: [''],
    download_delay: 1,
    concurrent_requests: 8,
    is_active: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    const newErrors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Spider name is required'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Spider description is required'
    }
    
    if (!formData.project) {
      newErrors.project = 'Project selection is required'
    }
    
    const validStartUrls = formData.start_urls.filter(url => url.trim())
    if (validStartUrls.length === 0) {
      newErrors.start_urls = 'At least one start URL is required'
    }
    
    const validDomains = formData.allowed_domains.filter(domain => domain.trim())
    if (validDomains.length === 0) {
      newErrors.allowed_domains = 'At least one allowed domain is required'
    }
    
    if (formData.download_delay < 0 || formData.download_delay > 60) {
      newErrors.download_delay = 'Download delay must be between 0 and 60 seconds'
    }
    
    if (formData.concurrent_requests < 1 || formData.concurrent_requests > 50) {
      newErrors.concurrent_requests = 'Concurrent requests must be between 1 and 50'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      onSubmit({
        name: formData.name.trim(),
        description: formData.description.trim(),
        project: formData.project,
        start_urls: validStartUrls,
        allowed_domains: validDomains,
        custom_settings: {
          download_delay: formData.download_delay,
          concurrent_requests: formData.concurrent_requests
        },
        is_active: formData.is_active
      })
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        project: '',
        start_urls: [''],
        allowed_domains: [''],
        download_delay: 1,
        concurrent_requests: 8,
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

  const handleArrayChange = (field: 'start_urls' | 'allowed_domains', index: number, value: string) => {
    const newArray = [...formData[field]]
    newArray[index] = value
    handleChange(field, newArray)
  }

  const addArrayItem = (field: 'start_urls' | 'allowed_domains') => {
    handleChange(field, [...formData[field], ''])
  }

  const removeArrayItem = (field: 'start_urls' | 'allowed_domains', index: number) => {
    if (formData[field].length > 1) {
      const newArray = formData[field].filter((_, i) => i !== index)
      handleChange(field, newArray)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Create New Spider</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Spider Name *
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
                  placeholder="Enter spider name"
                />
                {errors.name && (
                  <p className="text-red-500 text-xs mt-1">{errors.name}</p>
                )}
              </div>

              <div>
                <label htmlFor="project" className="block text-sm font-medium text-gray-700 mb-1">
                  Project *
                </label>
                <select
                  id="project"
                  value={formData.project}
                  onChange={(e) => handleChange('project', e.target.value)}
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
                placeholder="Describe what this spider will collect"
              />
              {errors.description && (
                <p className="text-red-500 text-xs mt-1">{errors.description}</p>
              )}
            </div>

            {/* Start URLs */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Start URLs *
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addArrayItem('start_urls')}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  Add URL
                </Button>
              </div>
              <div className="space-y-2">
                {formData.start_urls.map((url, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => handleArrayChange('start_urls', index, e.target.value)}
                      className="flex-1 h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
                      placeholder="https://example.com"
                    />
                    {formData.start_urls.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeArrayItem('start_urls', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              {errors.start_urls && (
                <p className="text-red-500 text-xs mt-1">{errors.start_urls}</p>
              )}
            </div>

            {/* Allowed Domains */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Allowed Domains *
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addArrayItem('allowed_domains')}
                >
                  <Plus className="h-3 w-3 mr-1" />
                  Add Domain
                </Button>
              </div>
              <div className="space-y-2">
                {formData.allowed_domains.map((domain, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={domain}
                      onChange={(e) => handleArrayChange('allowed_domains', index, e.target.value)}
                      className="flex-1 h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
                      placeholder="example.com"
                    />
                    {formData.allowed_domains.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeArrayItem('allowed_domains', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              {errors.allowed_domains && (
                <p className="text-red-500 text-xs mt-1">{errors.allowed_domains}</p>
              )}
            </div>

            {/* Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="download_delay" className="block text-sm font-medium text-gray-700 mb-1">
                  Download Delay (seconds)
                </label>
                <input
                  type="number"
                  id="download_delay"
                  min="0"
                  max="60"
                  step="0.1"
                  value={formData.download_delay}
                  onChange={(e) => handleChange('download_delay', parseFloat(e.target.value))}
                  className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                    errors.download_delay 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                />
                {errors.download_delay && (
                  <p className="text-red-500 text-xs mt-1">{errors.download_delay}</p>
                )}
              </div>

              <div>
                <label htmlFor="concurrent_requests" className="block text-sm font-medium text-gray-700 mb-1">
                  Concurrent Requests
                </label>
                <input
                  type="number"
                  id="concurrent_requests"
                  min="1"
                  max="50"
                  value={formData.concurrent_requests}
                  onChange={(e) => handleChange('concurrent_requests', parseInt(e.target.value))}
                  className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                    errors.concurrent_requests 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                />
                {errors.concurrent_requests && (
                  <p className="text-red-500 text-xs mt-1">{errors.concurrent_requests}</p>
                )}
              </div>
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
                Enable spider immediately
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                Create Spider
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}