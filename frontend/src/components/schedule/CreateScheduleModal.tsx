'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { X, Info } from 'lucide-react'
import { Schedule, Spider } from '@/types'

interface CreateScheduleModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (schedule: Partial<Schedule>) => void
  spiders: Spider[]
}

const CRON_PRESETS = [
  { label: 'Every minute', value: '* * * * *', description: 'Runs every minute' },
  { label: 'Every 5 minutes', value: '*/5 * * * *', description: 'Runs every 5 minutes' },
  { label: 'Every 15 minutes', value: '*/15 * * * *', description: 'Runs every 15 minutes' },
  { label: 'Every hour', value: '0 * * * *', description: 'Runs at minute 0 of every hour' },
  { label: 'Every 6 hours', value: '0 */6 * * *', description: 'Runs every 6 hours' },
  { label: 'Daily at 9 AM', value: '0 9 * * *', description: 'Runs daily at 9:00 AM' },
  { label: 'Daily at midnight', value: '0 0 * * *', description: 'Runs daily at midnight' },
  { label: 'Weekly (Sunday)', value: '0 0 * * 0', description: 'Runs weekly on Sunday at midnight' },
  { label: 'Monthly', value: '0 0 1 * *', description: 'Runs monthly on the 1st at midnight' },
]

export default function CreateScheduleModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  spiders 
}: CreateScheduleModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    spider: '',
    cron_expression: '0 * * * *',
    is_enabled: true,
    use_preset: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showCronHelp, setShowCronHelp] = useState(false)

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    const newErrors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Schedule name is required'
    }
    
    if (!formData.spider) {
      newErrors.spider = 'Spider selection is required'
    }
    
    if (!formData.cron_expression.trim()) {
      newErrors.cron_expression = 'Cron expression is required'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      onSubmit({
        name: formData.name.trim(),
        spider: formData.spider,
        cron_expression: formData.cron_expression.trim(),
        is_enabled: formData.is_enabled
      })
      
      // Reset form
      setFormData({
        name: '',
        spider: '',
        cron_expression: '0 * * * *',
        is_enabled: true,
        use_preset: true
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

  const handlePresetChange = (preset: string) => {
    handleChange('cron_expression', preset)
  }

  const selectedPreset = CRON_PRESETS.find(p => p.value === formData.cron_expression)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Create New Schedule</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Schedule Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Schedule Name *
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
                placeholder="Enter schedule name"
              />
              {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
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
                className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 ${
                  errors.spider 
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                }`}
              >
                <option value="">Select a spider</option>
                {spiders.filter(s => s.is_active).map(spider => (
                  <option key={spider.id} value={spider.id}>
                    {spider.name}
                  </option>
                ))}
              </select>
              {errors.spider && (
                <p className="text-red-500 text-xs mt-1">{errors.spider}</p>
              )}
            </div>

            {/* Cron Expression Mode Toggle */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Schedule Configuration
              </label>
              <div className="flex items-center space-x-4 mb-3">
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={formData.use_preset}
                    onChange={() => handleChange('use_preset', true)}
                    className="mr-2"
                  />
                  <span className="text-sm">Use Preset</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={!formData.use_preset}
                    onChange={() => handleChange('use_preset', false)}
                    className="mr-2"
                  />
                  <span className="text-sm">Custom Cron</span>
                </label>
              </div>
            </div>

            {/* Preset Selection */}
            {formData.use_preset ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Schedule Frequency *
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto border rounded-md">
                  {CRON_PRESETS.map((preset) => (
                    <label
                      key={preset.value}
                      className={`flex items-center p-3 cursor-pointer hover:bg-gray-50 ${
                        formData.cron_expression === preset.value ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                    >
                      <input
                        type="radio"
                        value={preset.value}
                        checked={formData.cron_expression === preset.value}
                        onChange={() => handlePresetChange(preset.value)}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-sm">{preset.label}</div> 
                        <div className="text-xs text-gray-500">{preset.description}</div>
                        <div className="text-xs text-gray-400 font-mono mt-1">{preset.value}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ) : (
              /* Custom Cron Expression */
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label htmlFor="cron_expression" className="block text-sm font-medium text-gray-700">
                    Cron Expression *
                  </label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowCronHelp(!showCronHelp)}
                  >
                    <Info className="h-4 w-4 mr-1" />
                    Help
                  </Button>
                </div>
                <input
                  type="text"
                  id="cron_expression"
                  value={formData.cron_expression}
                  onChange={(e) => handleChange('cron_expression', e.target.value)}
                  className={`w-full h-10 px-3 border rounded-md focus:outline-none focus:ring-1 font-mono text-sm ${
                    errors.cron_expression 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                  placeholder="0 * * * *"
                />
                {errors.cron_expression && (
                  <p className="text-red-500 text-xs mt-1">{errors.cron_expression}</p>
                )}
                
                {showCronHelp && (
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-md text-xs">
                    <div className="font-medium mb-2">Cron Expression Format:</div>
                    <div className="font-mono mb-2">minute hour day month weekday</div>
                    <div className="space-y-1">
                      <div>* = any value</div>
                      <div>*/5 = every 5 units</div>
                      <div>0-59 = minute (0-59)</div>
                      <div>0-23 = hour (0-23)</div>
                      <div>1-31 = day of month</div>
                      <div>1-12 = month</div>
                      <div>0-7 = day of week (0,7=Sunday)</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Preview */}
            {selectedPreset && formData.use_preset && (
              <div className="bg-green-50 border border-green-200 rounded-md p-3">
                <div className="text-sm font-medium text-green-800 mb-1">Preview:</div>
                <div className="text-sm text-green-700">{selectedPreset.description}</div>
              </div>
            )}

            {/* Enable Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_enabled"
                checked={formData.is_enabled}
                onChange={(e) => handleChange('is_enabled', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_enabled" className="ml-2 block text-sm text-gray-700">
                Enable schedule immediately
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                Create Schedule
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}