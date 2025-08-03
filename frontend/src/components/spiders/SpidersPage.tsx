'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import SpiderCard from '@/components/spiders/SpiderCard'
import CreateSpiderModal from '@/components/spiders/CreateSpiderModal'
import { Button } from '@/components/ui/Button'
import { Plus, Search, Filter } from 'lucide-react'
import { mockSpiders, mockProjects } from '@/lib/mockData'
import { Spider } from '@/types'

export default function SpidersPage() {
  const [spiders, setSpiders] = useState<Spider[]>(mockSpiders)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterProject, setFilterProject] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all')

  const filteredSpiders = spiders.filter(spider => {
    const matchesSearch = spider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         spider.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesProject = filterProject === 'all' || spider.project === filterProject
    const matchesStatus = filterStatus === 'all' ||
                         (filterStatus === 'active' && spider.is_active) ||
                         (filterStatus === 'inactive' && !spider.is_active)
    return matchesSearch && matchesProject && matchesStatus
  })

  const handleCreateSpider = (spiderData: Partial<Spider>) => {
    const newSpider: Spider = {
      id: Date.now().toString(),
      name: spiderData.name || '',
      description: spiderData.description || '',
      project: spiderData.project || '',
      start_urls: spiderData.start_urls || [],
      allowed_domains: spiderData.allowed_domains || [],
      custom_settings: spiderData.custom_settings || {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
      success_rate: 0,
      total_requests: 0,
      ...spiderData
    }
    setSpiders([newSpider, ...spiders])
    setIsCreateModalOpen(false)
  }

  const handleUpdateSpider = (updatedSpider: Spider) => {
    setSpiders(spiders.map(s => s.id === updatedSpider.id ? updatedSpider : s))
  }

  const handleDeleteSpider = (spiderId: string) => {
    setSpiders(spiders.filter(s => s.id !== spiderId))
  }

  const handleRunSpider = (spiderId: string) => {
    // Mock running spider functionality
    console.log('Running spider:', spiderId)
    // This would create a new job in a real implementation
  }

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
                <h1 className="text-2xl font-bold text-gray-900">Spiders</h1>
                <p className="text-gray-600">Configure and manage your web spiders</p>
              </div>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Spider
              </Button>
            </div>

            {/* Search and Filter Bar */}
            <div className="flex items-center space-x-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search spiders..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-10 w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <select
                  value={filterProject}
                  onChange={(e) => setFilterProject(e.target.value)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Projects</option>
                  {mockProjects.map(project => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
                
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active Only</option>
                  <option value="inactive">Inactive Only</option>
                </select>
              </div>
            </div>
          </div>

          {/* Stats Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 border">
              <div className="text-2xl font-bold text-blue-600">{spiders.length}</div>
              <div className="text-sm text-gray-600">Total Spiders</div>
            </div>
            <div className="bg-white rounded-lg p-4 border">
              <div className="text-2xl font-bold text-green-600">
                {spiders.filter(s => s.is_active).length}
              </div>
              <div className="text-sm text-gray-600">Active Spiders</div>
            </div>
            <div className="bg-white rounded-lg p-4 border">
              <div className="text-2xl font-bold text-orange-600">
                {spiders.reduce((sum, s) => sum + s.total_requests, 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Total Requests</div>
            </div>
            <div className="bg-white rounded-lg p-4 border">
              <div className="text-2xl font-bold text-purple-600">
                {spiders.length > 0 ? (spiders.reduce((sum, s) => sum + s.success_rate, 0) / spiders.length).toFixed(1) : 0}%
              </div>
              <div className="text-sm text-gray-600">Avg Success Rate</div>
            </div>
          </div>

          {/* Spiders Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredSpiders.map((spider) => (
              <SpiderCard
                key={spider.id}
                spider={spider}
                onUpdate={handleUpdateSpider}
                onDelete={handleDeleteSpider}
                onRun={handleRunSpider}
              />
            ))}
            
            {filteredSpiders.length === 0 && (
              <div className="col-span-full text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Plus className="h-12 w-12 mx-auto mb-4" />
                  <p className="text-lg font-medium">No spiders found</p>
                  <p className="text-sm">Create your first spider to start collecting data</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  Create Spider
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>

      <CreateSpiderModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateSpider}
        projects={mockProjects}
      />
    </div>
  )
}