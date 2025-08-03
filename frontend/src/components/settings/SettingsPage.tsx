'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Server, 
  Shield, 
  Globe,
  Database,
  Bell,
  User
} from 'lucide-react'
import { mockProxies } from '@/lib/mockData'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('proxies')
  const [proxies, setProxies] = useState(mockProxies)

  const tabs = [
    { id: 'proxies', name: 'Proxies', icon: Globe },
    { id: 'database', name: 'Database', icon: Database },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'system', name: 'System', icon: Server },
  ]

  const renderProxiesTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Proxy Configuration</h3>
          <p className="text-sm text-gray-600">Manage proxy servers for web scraping</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Proxy
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {proxies.map((proxy) => (
          <Card key={proxy.id}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{proxy.name}</CardTitle>
                <Badge variant={proxy.is_active ? 'default' : 'secondary'}>
                  {proxy.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="text-gray-600">Host:</span>
                  <span className="ml-2 font-mono">{proxy.host}:{proxy.port}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-600">Type:</span>
                  <span className="ml-2 uppercase">{proxy.proxy_type}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-600">Success Rate:</span>
                  <span className={`ml-2 ${proxy.success_rate >= 95 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {proxy.success_rate}%
                  </span>
                </div>
                {proxy.last_used && (
                  <div className="text-sm">
                    <span className="text-gray-600">Last Used:</span>
                    <span className="ml-2">{new Date(proxy.last_used).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
              <div className="flex justify-end space-x-2 mt-4">
                <Button variant="ghost" size="sm">
                  <Edit className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="text-red-600">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderDatabaseTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Database Settings</h3>
        <p className="text-sm text-gray-600">Configure database connections and maintenance</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Connection Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Database URL
              </label>
              <input
                type="text"
                defaultValue="postgresql://localhost:5432/webscraper"
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Connection Pool Size
              </label>
              <input
                type="number"
                defaultValue={20}
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Maintenance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto-cleanup old responses</p>
                <p className="text-sm text-gray-600">Delete responses older than 90 days</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Compress old data</p>
                <p className="text-sm text-gray-600">Compress data older than 30 days</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            <Button variant="outline">Run Maintenance Now</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Notification Settings</h3>
        <p className="text-sm text-gray-600">Configure alerts and notifications</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Email Notifications</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Job completion notifications</p>
              <p className="text-sm text-gray-600">Get notified when jobs finish</p>
            </div>
            <input type="checkbox" defaultChecked className="rounded" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Error alerts</p>
              <p className="text-sm text-gray-600">Get notified about failed jobs</p>
            </div>
            <input type="checkbox" defaultChecked className="rounded" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Weekly reports</p>
              <p className="text-sm text-gray-600">Receive weekly performance summaries</p>
            </div>
            <input type="checkbox" className="rounded" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notification Email
            </label>
            <input
              type="email"
              defaultValue="admin@example.com"
              className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <Button>Save Settings</Button>
        </CardContent>
      </Card>
    </div>
  )

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Security Settings</h3>
        <p className="text-sm text-gray-600">Manage authentication and security options</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Authentication</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Two-factor authentication</p>
                <p className="text-sm text-gray-600">Add extra security to your account</p>
              </div>
              <Button variant="outline" size="sm">Enable</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Session timeout</p>
                <p className="text-sm text-gray-600">Auto logout after inactivity</p>
              </div>
              <select className="border border-gray-300 rounded px-2 py-1 text-sm">
                <option>30 minutes</option>
                <option>1 hour</option>
                <option>4 hours</option>
                <option>8 hours</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                JWT Secret Key
              </label>
              <input
                type="password"
                defaultValue="********************************"
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <Button>Update Security</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API Access</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">API Rate Limiting</p>
                <p className="text-sm text-gray-600">Limit API requests per minute</p>
              </div>
              <input
                type="number"
                defaultValue={100}
                className="w-20 h-8 px-2 border border-gray-300 rounded text-sm"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">CORS Origins</p>
                <p className="text-sm text-gray-600">Allowed origins for API access</p>
              </div>
              <Button variant="outline" size="sm">Configure</Button>
            </div>
            <div>
              <p className="font-medium mb-2">Active API Keys</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="font-mono text-sm">sk_test_4eC39Hq...09d</span>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    Revoke
                  </Button>
                </div>
              </div>
              <Button variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Generate New Key
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderSystemTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">System Settings</h3>
        <p className="text-sm text-gray-600">Configure system-wide settings and monitoring</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Default Request Delay (seconds)
              </label>
              <input
                type="number"
                defaultValue={1}
                step="0.1"
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Concurrent Jobs
              </label>
              <input
                type="number"
                defaultValue={10}
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Worker Poll Interval (seconds)
              </label>
              <input
                type="number"
                defaultValue={5}
                className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <Button>Save Performance Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Logging & Monitoring</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Log Level
              </label>
              <select className="w-full h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:border-blue-500 focus:ring-blue-500">
                <option>DEBUG</option>
                <option>INFO</option>
                <option>WARNING</option>
                <option>ERROR</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Enable request logging</p>
                <p className="text-sm text-gray-600">Log all HTTP requests</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Performance monitoring</p>
                <p className="text-sm text-gray-600">Track system performance metrics</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            
            <div>
              <p className="font-medium mb-2">System Status</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>CPU Usage:</span>
                  <span className="text-green-600">23%</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory Usage:</span>
                  <span className="text-yellow-600">67%</span>
                </div>
                <div className="flex justify-between">
                  <span>Disk Usage:</span>
                  <span className="text-green-600">34%</span>
                </div>
                <div className="flex justify-between">
                  <span>Active Workers:</span>
                  <span className="text-blue-600">3</span>
                </div>
              </div>
            </div>
            
            <Button>Save Monitoring Settings</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'proxies': return renderProxiesTab()
      case 'database': return renderDatabaseTab()
      case 'notifications': return renderNotificationsTab()
      case 'security': return renderSecurityTab()
      case 'system': return renderSystemTab()
      default: return renderProxiesTab()
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-6">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Configure system settings and preferences</p>
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Settings Navigation */}
            <div className="lg:w-64 flex-shrink-0">
              <Card>
                <CardContent className="p-0">
                  <nav className="space-y-1">
                    {tabs.map((tab) => {
                      const Icon = tab.icon
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
                            activeTab === tab.id
                              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                        >
                          <Icon className="mr-3 h-5 w-5" />
                          {tab.name}
                        </button>
                      )
                    })}
                  </nav>
                </CardContent>
              </Card>
            </div>

            {/* Settings Content */}
            <div className="flex-1">
              {renderTabContent()}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}