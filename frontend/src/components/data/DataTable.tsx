'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { 
  ChevronUp, 
  ChevronDown, 
  Eye, 
  Download,
  ExternalLink,
  Clock,
  HardDrive
} from 'lucide-react'

interface ResponseData {
  id: string
  url: string
  status_code: number
  size: number
  response_time: number
  created_at: string
  job: string
  spider: string
  success: boolean
}

interface DataTableProps {
  responses: ResponseData[]
  onSort: (field: string) => void
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

export default function DataTable({ responses, onSort, sortBy, sortOrder }: DataTableProps) {
  const [selectedResponse, setSelectedResponse] = useState<ResponseData | null>(null)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getStatusBadge = (statusCode: number, success: boolean) => {
    if (success && statusCode >= 200 && statusCode < 300) {
      return <Badge className="bg-green-100 text-green-800">{statusCode}</Badge>
    }
    if (statusCode >= 400) {
      return <Badge className="bg-red-100 text-red-800">{statusCode}</Badge>
    }
    if (statusCode >= 300) {
      return <Badge className="bg-yellow-100 text-yellow-800">{statusCode}</Badge>
    }
    return <Badge variant="outline">{statusCode}</Badge>
  }

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy !== field) return null
    return sortOrder === 'asc' ? 
      <ChevronUp className="h-4 w-4" /> : 
      <ChevronDown className="h-4 w-4" />
  }

  return (
    <div className="space-y-4">
      {/* Table Header */}
      <Card>
        <CardContent className="p-0">
          <div className="grid grid-cols-12 gap-4 p-4 bg-gray-50 border-b text-sm font-medium text-gray-600">
            <div className="col-span-4">
              <button 
                onClick={() => onSort('url')}
                className="flex items-center space-x-1 hover:text-gray-900"
              >
                <span>URL</span>
                <SortIcon field="url" />
              </button>
            </div>
            <div className="col-span-2">
              <button 
                onClick={() => onSort('status_code')}
                className="flex items-center space-x-1 hover:text-gray-900"
              >
                <span>Status</span>
                <SortIcon field="status_code" />
              </button>
            </div>
            <div className="col-span-1">
              <button 
                onClick={() => onSort('size')}
                className="flex items-center space-x-1 hover:text-gray-900"
              >
                <span>Size</span>
                <SortIcon field="size" />
              </button>
            </div>
            <div className="col-span-1">
              <button 
                onClick={() => onSort('response_time')}
                className="flex items-center space-x-1 hover:text-gray-900"
              >
                <span>Time</span>
                <SortIcon field="response_time" />
              </button>
            </div>
            <div className="col-span-2">
              <button 
                onClick={() => onSort('created_at')}
                className="flex items-center space-x-1 hover:text-gray-900"
              >
                <span>Date</span>
                <SortIcon field="created_at" />
              </button>
            </div>
            <div className="col-span-2">Actions</div>
          </div>
        </CardContent>
      </Card>

      {/* Table Rows */}
      {responses.map((response) => (
        <Card key={response.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="grid grid-cols-12 gap-4 items-center">
              <div className="col-span-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-900 truncate" title={response.url}>
                    {response.url}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{response.spider}</span>
                    <span>•</span>
                    <span>{response.job}</span>
                  </div>
                </div>
              </div>
              
              <div className="col-span-2">
                {getStatusBadge(response.status_code, response.success)}
              </div>
              
              <div className="col-span-1">
                <div className="flex items-center text-sm text-gray-900">
                  <HardDrive className="h-3 w-3 mr-1 text-gray-400" />
                  {formatSize(response.size)}
                </div>
              </div>
              
              <div className="col-span-1">
                <div className="flex items-center text-sm text-gray-900">
                  <Clock className="h-3 w-3 mr-1 text-gray-400" />
                  {response.response_time}ms
                </div>
              </div>
              
              <div className="col-span-2">
                <p className="text-sm text-gray-600">
                  {formatDate(response.created_at)}
                </p>
              </div>
              
              <div className="col-span-2">
                <div className="flex items-center space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedResponse(response)}
                    title="View details"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(response.url, '_blank')}
                    title="Open URL"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => console.log('Download response:', response.id)}
                    title="Download response"
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {responses.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <HardDrive className="h-12 w-12 mx-auto mb-4" />
              <p className="text-lg font-medium">No data found</p>
                                <p className="text-sm">Run some spiders to see response data here</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Response Details Modal */}
      {selectedResponse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Response Details</h3>
                <Button variant="ghost" onClick={() => setSelectedResponse(null)}>
                  ×
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">URL</label>
                  <p className="text-sm text-gray-900 font-mono break-all">
                    {selectedResponse.url}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status Code</label>
                    <p className="text-sm text-gray-900">{selectedResponse.status_code}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Response Time</label>
                    <p className="text-sm text-gray-900">{selectedResponse.response_time}ms</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Size</label>
                    <p className="text-sm text-gray-900">{formatSize(selectedResponse.size)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Success</label>
                    <p className="text-sm text-gray-900">
                      {selectedResponse.success ? 'Yes' : 'No'}
                    </p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-600">Job</label>
                  <p className="text-sm text-gray-900">{selectedResponse.job}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-600">Spider</label>
                  <p className="text-sm text-gray-900">{selectedResponse.spider}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-600">Created</label>
                  <p className="text-sm text-gray-900">
                    {new Date(selectedResponse.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <Button variant="outline" onClick={() => setSelectedResponse(null)}>
                  Close
                </Button>
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}