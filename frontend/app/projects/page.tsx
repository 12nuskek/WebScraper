"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { useCreateModal } from "@/components/create-modal-context"

function ProjectsPageContent() {
  const { openProjectForm } = useCreateModal()

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🏗️ Projects Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">8 Active Projects</p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search projects..."
            className="w-full px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent"
          />
        </div>
        <select className="px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring">
          <option>Status: All</option>
          <option>Active</option>
          <option>Paused</option>
          <option>Warning</option>
        </select>
        <select className="px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring">
          <option>Category: All</option>
          <option>E-commerce</option>
          <option>Market Analysis</option>
          <option>Social Media</option>
        </select>
        <button
          onClick={openProjectForm}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 font-medium"
        >
          + New
        </button>
      </div>

      {/* Project Cards */}
      <div className="space-y-6">
        {/* LEGO Project Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🧱 LEGO Market Analysis</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🟢 Active
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Comprehensive LEGO pricing and sentiment analysis</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Created: 5 days ago</span>
            <span>•</span>
            <span>Last Update: 2 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="font-semibold">47,231 collected</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Quality Score</p>
              <p className="font-semibold text-green-600">96.7% (Excellent)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Spiders</p>
              <p className="font-semibold">4/4 running</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Team Members</p>
              <p className="font-semibold">3 analysts</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Recent Activity:</p>
            <div className="space-y-1 text-sm text-gray-600">
              <p>• 2 min: BigW pricing update completed</p>
              <p>• 15 min: Price anomaly detected (Creator Expert +15%)</p>
              <p>• 1 hr: Weekly quality report generated</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 Open Dashboard
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⚙️ Configure
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              👥 Team
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Analytics
            </button>
          </div>
        </div>

        {/* Sneaker Project Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">👟 Sneaker Resale Intelligence</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  🟡 Warning
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Athletic footwear market analysis</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Created: 12 days ago</span>
            <span>•</span>
            <span>Last Update: 45 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="font-semibold">89,456 collected</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Quality Score</p>
              <p className="font-semibold text-yellow-600">87.3% (Needs attention)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Spiders</p>
              <p className="font-semibold text-red-600">3/5 running (2 failed)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Team Members</p>
              <p className="font-semibold">2 analysts</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Issues:</p>
            <div className="space-y-1 text-sm text-yellow-700">
              <p>⚠️ StockX spider experiencing rate limits</p>
              <p>⚠️ GOAT API integration needs authentication refresh</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-destructive text-destructive-foreground rounded text-sm hover:bg-destructive/90">
              🔧 Fix Issues
            </button>
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 Dashboard
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⚙️ Configure
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              👥 Team
            </button>
          </div>
        </div>

        {/* Wine Project Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🍷 Wine Investment Tracker</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  ⏸️ Paused
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Fine wine market and auction analysis</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Created: 28 days ago</span>
            <span>•</span>
            <span>Last Update: 3 days ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="font-semibold">34,567 collected</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Quality Score</p>
              <p className="font-semibold text-green-600">94.1% (Good)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Spiders</p>
              <p className="font-semibold text-gray-600">0/6 (manually paused)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Team Members</p>
              <p className="font-semibold">1 analyst</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Pause Reason:</p>
            <p className="text-sm text-gray-600">Quarterly data analysis phase</p>
            <p className="text-sm text-gray-600">Resume Scheduled: August 15, 2025</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700">▶️ Resume</button>
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 View Data
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⚙️ Configure
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Reports
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex items-center justify-center gap-4 mt-8 pt-6 border-t border-gray-200">
        <button className="px-4 py-2 text-primary hover:text-primary/80 font-medium">Load More Projects...</button>
        <button className="px-4 py-2 text-muted-foreground hover:text-foreground font-medium">
          📈 View All Analytics
        </button>
        <button className="px-4 py-2 text-muted-foreground hover:text-foreground font-medium">📋 Export List</button>
      </div>
    </div>
  )
}

export default function ProjectsPage() {
  return (
    <DashboardLayout>
      <ProjectsPageContent />
    </DashboardLayout>
  )
}
