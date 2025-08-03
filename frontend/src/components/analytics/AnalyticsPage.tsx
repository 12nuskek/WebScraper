'use client'

import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import ChartPlaceholder from '@/components/dashboard/ChartPlaceholder'
import StatCard from '@/components/dashboard/StatCard'
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Database,
  Globe,
  Target,
  Activity,
  AlertCircle
} from 'lucide-react'

export default function AnalyticsPage() {
  // Mock analytics data
  const performanceMetrics = {
    avgResponseTime: 245,
    successRate: 98.2,
    totalRequests: 15420,
    dataPoints: 1247890,
    errorRate: 1.8,
    uptime: 99.5
  }

  const domainStats = [
    { domain: 'amazon.com', requests: 5420, success: 98.5, avgTime: 234 },
    { domain: 'ebay.com', requests: 3210, success: 95.2, avgTime: 189 },
    { domain: 'news.com', requests: 2890, success: 99.1, avgTime: 156 },
    { domain: 'social.com', requests: 1820, success: 96.8, avgTime: 267 },
    { domain: 'shop.com', requests: 1180, success: 94.3, avgTime: 298 }
  ]

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-6">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600">Performance metrics and insights</p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <StatCard
              title="Avg Response Time"
              value={`${performanceMetrics.avgResponseTime}ms`}
              change="-12ms from last week"
              changeType="positive"
              icon={Clock}
            />
            <StatCard
              title="Success Rate"
              value={`${performanceMetrics.successRate}%`}
              change="+0.3% from yesterday"
              changeType="positive"
              icon={TrendingUp}
            />
            <StatCard
              title="Total Requests"
              value={performanceMetrics.totalRequests.toLocaleString()}
              change="+1,234 from yesterday"
              changeType="positive"
              icon={Globe}
            />
            <StatCard
              title="Data Points"
              value={performanceMetrics.dataPoints.toLocaleString()}
              change="+15.2% from last month"
              changeType="positive"
              icon={Database}
            />
          </div>

          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <ChartPlaceholder 
              title="Request Volume Over Time"
              description="Daily request counts and success rates"
              height={300}
            />
            <ChartPlaceholder 
              title="Response Time Distribution"
              description="Response time percentiles and trends"
              height={300}
            />
          </div>

          {/* Charts Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <ChartPlaceholder 
              title="Success Rate by Hour"
              description="Hourly success rate patterns"
              height={250}
            />
            <ChartPlaceholder 
              title="Error Types"
              description="Distribution of error codes"
              height={250}
            />
            <ChartPlaceholder 
              title="Data Growth"
              description="Cumulative data collection"
              height={250}
            />
          </div>

          {/* Domain Performance Table */}
          <div className="bg-white rounded-lg border mb-6">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Performance by Domain</h3>
              <p className="text-sm text-gray-600 mt-1">Success rates and response times by target domain</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Domain
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Requests
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Success Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Response Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {domainStats.map((domain, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Globe className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm font-medium text-gray-900">{domain.domain}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {domain.requests.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className={`text-sm font-medium ${
                            domain.success >= 98 ? 'text-green-600' :
                            domain.success >= 95 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {domain.success}%
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {domain.avgTime}ms
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          domain.success >= 98 ? 'bg-green-100 text-green-800' :
                          domain.success >= 95 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {domain.success >= 98 ? 'Excellent' :
                           domain.success >= 95 ? 'Good' : 'Needs Attention'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Performance Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <TrendingUp className="h-5 w-5 text-green-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Response times improved</p>
                    <p className="text-sm text-gray-600">Average response time decreased by 12ms this week</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Target className="h-5 w-5 text-blue-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">High success rate maintained</p>
                    <p className="text-sm text-gray-600">Success rate has been above 98% for 7 days</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Activity className="h-5 w-5 text-purple-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Peak hours identified</p>
                    <p className="text-sm text-gray-600">Best performance between 2-6 AM UTC</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Optimize shop.com scraping</p>
                    <p className="text-sm text-gray-600">Consider increasing delays for better success rate</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Clock className="h-5 w-5 text-blue-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Schedule during off-peak hours</p>
                    <p className="text-sm text-gray-600">Move heavy scraping jobs to 2-6 AM for better performance</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Database className="h-5 w-5 text-green-500 mt-0.5 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Archive old data</p>
                    <p className="text-sm text-gray-600">Consider archiving responses older than 90 days</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}