'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import DataTable from '@/components/data/DataTable'
import { Button } from '@/components/ui/Button'
import { Search, Filter, Download, RefreshCw } from 'lucide-react'
import { mockProjects } from '@/lib/mockData'

// Mock response data
const mockResponses = [
  {
    id: '1',
    url: 'https://example.com/product/123',
    status_code: 200,
    size: 45320,
    response_time: 245,
    created_at: '2024-01-20T15:30:00Z',
    job: 'Daily Product Scrape',
    spider: 'Amazon Product Spider',
    success: true
  },
  {
    id: '2',
    url: 'https://example.com/product/124',
    status_code: 404,
    size: 1234,
    response_time: 156,
    created_at: '2024-01-20T15:25:00Z',
    job: 'Daily Product Scrape',
    spider: 'Amazon Product Spider',
    success: false
  },
  {
    id: '3',
    url: 'https://news.example.com/article/456',
    status_code: 200,
    size: 78234,
    response_time: 189,
    created_at: '2024-01-20T14:45:00Z',
    job: 'News Collection',
    spider: 'News Spider',
    success: true
  }
]

export default function DataPage() {
  const [responses] = useState(mockResponses)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterProject, setFilterProject] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const filteredResponses = responses.filter(response => {
    const matchesSearch = response.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         response.job.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         response.spider.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = filterStatus === 'all' ||
                         (filterStatus === 'success' && response.success) ||
                         (filterStatus === 'error' && !response.success)
    
    return matchesSearch && matchesStatus
  }).sort((a, b) => {
    const aVal = a[sortBy as keyof typeof a]
    const bVal = b[sortBy as keyof typeof b]
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1
    }
    return aVal < bVal ? 1 : -1
  })

  const successCount = responses.filter(r => r.success).length
  const errorCount = responses.filter(r => !r.success).length
  const avgResponseTime = responses.reduce((sum, r) => sum + r.response_time, 0) / responses.length
  const totalSize = responses.reduce((sum, r) => sum + r.size, 0)

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
                <h1 className="text-2xl font-bold text-gray-900">Data</h1>
                <p className="text-gray-600">View and manage scraped responses and data</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button variant="outline" onClick={() => window.location.reload()}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Export Data
                </Button>
              </div>
            </div>

            {/* Search and Filter Bar */}
            <div className="flex items-center space-x-4 mb-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search responses..."
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
                  <option value="success">Successful</option>
                  <option value="error">Errors</option>
                </select>
                
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="h-10 rounded-md border border-gray-300 bg-white px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="created_at">Sort by Date</option>
                  <option value="response_time">Sort by Response Time</option>
                  <option value="size">Sort by Size</option>
                  <option value="status_code">Sort by Status Code</option>
                </select>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </Button>
              </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-blue-600">{responses.length}</div>
                <div className="text-sm text-gray-600">Total Responses</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-green-600">{successCount}</div>
                <div className="text-sm text-gray-600">Successful</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-red-600">{errorCount}</div>
                <div className="text-sm text-gray-600">Errors</div>
              </div>
              <div className="bg-white rounded-lg p-4 border">
                <div className="text-2xl font-bold text-purple-600">{Math.round(avgResponseTime)}ms</div>
                <div className="text-sm text-gray-600">Avg Response Time</div>
              </div>
            </div>
          </div>

          {/* Data Table */}
          <DataTable 
            responses={filteredResponses}
            onSort={(field) => {
              if (sortBy === field) {
                setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
              } else {
                setSortBy(field)
                setSortOrder('desc')
              }
            }}
            sortBy={sortBy}
            sortOrder={sortOrder}
          />
        </main>
      </div>
    </div>
  )
}