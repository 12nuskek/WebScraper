'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import ScheduleCard from '@/components/schedule/ScheduleCard'
import CreateScheduleModal from '@/components/schedule/CreateScheduleModal'
import { Button } from '@/components/ui/Button'
import { Plus, Search, Filter, Clock } from 'lucide-react'
import { mockSchedules, mockSpiders } from '@/lib/mockData'
import { Schedule } from '@/types'

export default function SchedulePage() {
  const [schedules, setSchedules] = useState<Schedule[]>(mockSchedules)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'enabled' | 'disabled'>('all')

  const filteredSchedules = schedules.filter(schedule => {
    const spider = mockSpiders.find(s => s.id === schedule.spider)
    const matchesSearch = schedule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         spider?.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' ||
                         (filterStatus === 'enabled' && schedule.is_enabled) ||
                         (filterStatus === 'disabled' && !schedule.is_enabled)
    return matchesSearch && matchesStatus
  })

  const handleCreateSchedule = (scheduleData: Partial<Schedule>) => {
    const newSchedule: Schedule = {
      id: Date.now().toString(),
      name: scheduleData.name || '',
      spider: scheduleData.spider || '',
      cron_expression: scheduleData.cron_expression || '',
      is_enabled: scheduleData.is_enabled ?? true,
      next_run: calculateNextRun(scheduleData.cron_expression || ''),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      run_count: 0,
      ...scheduleData
    }
    setSchedules([newSchedule, ...schedules])
    setIsCreateModalOpen(false)
  }

  const handleUpdateSchedule = (updatedSchedule: Schedule) => {
    setSchedules(schedules.map(s => s.id === updatedSchedule.id ? updatedSchedule : s))
  }

  const handleDeleteSchedule = (scheduleId: string) => {
    setSchedules(schedules.filter(s => s.id !== scheduleId))
  }

  const handleToggleSchedule = (scheduleId: string) => {
    const schedule = schedules.find(s => s.id === scheduleId)
    if (schedule) {
      handleUpdateSchedule({
        ...schedule,
        is_enabled: !schedule.is_enabled,
        updated_at: new Date().toISOString()
      })
    }
  }

  const calculateNextRun = (cronExpression: string): string => {
    // Mock next run calculation - in real app, use a cron parser
    const now = new Date()
    now.setHours(now.getHours() + 1)
    return now.toISOString()
  }

  const enabledCount = schedules.filter(s => s.is_enabled).length
  const disabledCount = schedules.filter(s => !s.is_enabled).length
  const totalRuns = schedules.reduce((sum, s) => sum + s.run_count, 0)

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
                <h1 className="text-2xl font-bold text-gray-900">Schedules</h1>
                <p className="text-gray-600">Manage automated scraping schedules</p>
              </div>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Schedule
              </Button>
            </div>

            {/* Search and Filter Bar */}
            <div className="flex items-center space-x-4 mb-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search schedules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-10 w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Schedules</option>
                  <option value="enabled">Enabled Only</option>
                  <option value="disabled">Disabled Only</option>
                </select>
              </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-blue-600">{schedules.length}</div>
                <div className="text-sm text-gray-600">Total Schedules</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-green-600">{enabledCount}</div>
                <div className="text-sm text-gray-600">Enabled</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-gray-600">{disabledCount}</div>
                <div className="text-sm text-gray-600">Disabled</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-purple-600">{totalRuns}</div>
                <div className="text-sm text-gray-600">Total Runs</div>
              </div>
            </div>
          </div>

          {/* Schedules Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredSchedules.map((schedule) => (
              <ScheduleCard
                key={schedule.id}
                schedule={schedule}
                onUpdate={handleUpdateSchedule}
                onDelete={handleDeleteSchedule}
                onToggle={handleToggleSchedule}
              />
            ))}
            
            {filteredSchedules.length === 0 && (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Clock className="h-12 w-12 mx-auto mb-4" />
                  <p className="text-lg font-medium">No schedules found</p>
                  <p className="text-sm">Create your first schedule to automate scraping</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  Create Schedule
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>

      <CreateScheduleModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateSchedule}
        spiders={mockSpiders}
      />
    </div>
  )
}