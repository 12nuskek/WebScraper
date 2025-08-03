'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import JobCard from '@/components/jobs/JobCard'
import CreateJobModal from '@/components/jobs/CreateJobModal'
import JobDetailsModal from '@/components/jobs/JobDetailsModal'
import { Button } from '@/components/ui/Button'
import { Plus, Search, Filter, RefreshCw } from 'lucide-react'
import { mockJobs, mockSpiders, mockProjects } from '@/lib/mockData'
import { Job } from '@/types'

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>(mockJobs)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterProject, setFilterProject] = useState<string>('all')

  const filteredJobs = jobs.filter(job => {
    const spider = mockSpiders.find(s => s.id === job.spider)
    const project = mockProjects.find(p => p.id === job.project)
    
    const matchesSearch = job.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         spider?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project?.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || job.status === filterStatus
    const matchesProject = filterProject === 'all' || job.project === filterProject
    
    return matchesSearch && matchesStatus && matchesProject
  })

  const handleCreateJob = (jobData: Partial<Job>) => {
    const newJob: Job = {
      id: Date.now().toString(),
      name: jobData.name || '',
      spider: jobData.spider || '',
      project: jobData.project || '',
      status: 'queued',
      priority: jobData.priority || 5,
      created_at: new Date().toISOString(),
      progress: 0,
      items_scraped: 0,
      ...jobData
    }
    setJobs([newJob, ...jobs])
    setIsCreateModalOpen(false)
  }

  const handleUpdateJob = (updatedJob: Job) => {
    setJobs(jobs.map(j => j.id === updatedJob.id ? updatedJob : j))
  }

  const handleDeleteJob = (jobId: string) => {
    setJobs(jobs.filter(j => j.id !== jobId))
  }

  const handleCancelJob = (jobId: string) => {
    const job = jobs.find(j => j.id === jobId)
    if (job && (job.status === 'queued' || job.status === 'running')) {
      handleUpdateJob({ ...job, status: 'cancelled' })
    }
  }

  const handleRetryJob = (jobId: string) => {
    const job = jobs.find(j => j.id === jobId)
    if (job && job.status === 'failed') {
      handleUpdateJob({ 
        ...job, 
        status: 'queued',
        error_message: undefined,
        progress: 0
      })
    }
  }

  const getStatusCounts = () => {
    return {
      total: jobs.length,
      queued: jobs.filter(j => j.status === 'queued').length,
      running: jobs.filter(j => j.status === 'running').length,
      done: jobs.filter(j => j.status === 'done').length,
      failed: jobs.filter(j => j.status === 'failed').length,
      cancelled: jobs.filter(j => j.status === 'cancelled').length
    }
  }

  const statusCounts = getStatusCounts()

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
                <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
                <p className="text-gray-600">Monitor and manage scraping jobs</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button variant="outline" onClick={() => window.location.reload()}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Job
                </Button>
              </div>
            </div>

            {/* Search and Filter Bar */}
            <div className="flex items-center space-x-4 mb-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search jobs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-10 w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="queued">Queued</option>
                  <option value="running">Running</option>
                  <option value="done">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                
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
              </div>
            </div>

            {/* Status Overview */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-gray-900">{statusCounts.total}</div>
                <div className="text-sm text-gray-600">Total Jobs</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-yellow-600">{statusCounts.queued}</div>
                <div className="text-sm text-gray-600">Queued</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-blue-600">{statusCounts.running}</div>
                <div className="text-sm text-gray-600">Running</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-green-600">{statusCounts.done}</div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-red-600">{statusCounts.failed}</div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-gray-600">{statusCounts.cancelled}</div>
                <div className="text-sm text-gray-600">Cancelled</div>
              </div>
            </div>
          </div>

          {/* Jobs List */}
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onUpdate={handleUpdateJob}
                onDelete={handleDeleteJob}
                onCancel={handleCancelJob}
                onRetry={handleRetryJob}
                onViewDetails={setSelectedJob}
              />
            ))}
            
            {filteredJobs.length === 0 && (
              <div className="text-center py-12 bg-white rounded-lg border">
                <div className="text-gray-400 mb-4">
                  <Plus className="h-12 w-12 mx-auto mb-4" />
                  <p className="text-lg font-medium">No jobs found</p>
                  <p className="text-sm">Create your first job to start scraping</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  Create Job
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>

      <CreateJobModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateJob}
        projects={mockProjects}
        spiders={mockSpiders}
      />

      {selectedJob && (
        <JobDetailsModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onUpdate={handleUpdateJob}
        />
      )}
    </div>
  )
}