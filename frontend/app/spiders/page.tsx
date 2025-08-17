"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { useCreateModal } from "@/components/create-modal-context"
import Link from "next/link"

function SpidersPageContent() {
  const { openSpiderForm } = useCreateModal()

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🕷️ Spiders Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">23 Active Spiders</p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search spiders..."
            className="w-full px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent"
          />
        </div>
        <select className="px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring">
          <option>Status: All</option>
          <option>Running</option>
          <option>Paused</option>
          <option>Rate Limited</option>
          <option>Failed</option>
        </select>
        <select className="px-4 py-2 border border-input rounded-lg focus:ring-2 focus:ring-ring">
          <option>Type: All</option>
          <option>@browser</option>
          <option>@request</option>
          <option>@task</option>
        </select>
        <button
          onClick={openSpiderForm}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 font-medium"
        >
          + New Spider
        </button>
      </div>

      {/* Spider Cards */}
      <div className="space-y-6">
        {/* LEGO Official Spider */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🧱 LEGO Official Store</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🟢 Running
                </span>
                <span className="text-sm text-gray-600">•</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  @browser
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Scraping LEGO product data, pricing, and availability</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Target: lego.com</span>
            <span>•</span>
            <span>Created: 5 days ago</span>
            <span>•</span>
            <span>Last Run: 2 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Items/Hour</p>
              <p className="font-semibold text-green-600">2,347</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="font-semibold text-green-600">98.7%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Scraped</p>
              <p className="font-semibold">47,231 items</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Runtime</p>
              <p className="font-semibold">4d 12h 23m</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Recent Activity:</p>
            <div className="space-y-1 text-sm text-gray-600">
              <p>• 2 min: Batch completed (247 products)</p>
              <p>• 15 min: New product category detected</p>
              <p>• 1 hr: Performance optimization applied</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 View Data
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⏸️ Pause
            </button>
            <Link href="/spiders/lego-official-store">
              <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
                ⚙️ Configure
              </button>
            </Link>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Analytics
            </button>
          </div>
        </div>

        {/* BigW Spider */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🛒 BigW Product Monitor</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🟢 Running
                </span>
                <span className="text-sm text-gray-600">•</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  @request
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Lightweight API-based scraping for BigW pricing data</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Target: bigw.com.au</span>
            <span>•</span>
            <span>Created: 8 days ago</span>
            <span>•</span>
            <span>Last Run: 5 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Items/Hour</p>
              <p className="font-semibold text-green-600">1,847</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="font-semibold text-green-600">96.3%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Scraped</p>
              <p className="font-semibold">89,456 items</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Runtime</p>
              <p className="font-semibold">8d 4h 12m</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Recent Activity:</p>
            <div className="space-y-1 text-sm text-gray-600">
              <p>• 5 min: Price update batch completed</p>
              <p>• 30 min: API rate limit handled gracefully</p>
              <p>• 2 hr: Data validation passed</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 View Data
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⏸️ Pause
            </button>
            <Link href="/spiders/bigw-product-monitor">
              <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
                ⚙️ Configure
              </button>
            </Link>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Analytics
            </button>
          </div>
        </div>

        {/* Target Monitor Spider - Rate Limited */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🎯 Target Price Monitor</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  🟡 Rate Limited
                </span>
                <span className="text-sm text-gray-600">•</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  @browser
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Target.com product monitoring with anti-detection</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Target: target.com</span>
            <span>•</span>
            <span>Created: 3 days ago</span>
            <span>•</span>
            <span>Last Run: 12 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Items/Hour</p>
              <p className="font-semibold text-yellow-600">0 (paused)</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="font-semibold text-yellow-600">89.2%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Scraped</p>
              <p className="font-semibold">12,847 items</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Retry In</p>
              <p className="font-semibold text-yellow-600">4m 23s</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Issues:</p>
            <div className="space-y-1 text-sm text-yellow-700">
              <p>⚠️ Rate limit detected - implementing backoff strategy</p>
              <p>⚠️ Consider rotating proxy pool</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-orange-600 text-white rounded text-sm hover:bg-orange-700">
              🔧 Fix Issues
            </button>
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 View Data
            </button>
            <Link href="/spiders/target-price-monitor">
              <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
                ⚙️ Configure
              </button>
            </Link>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Analytics
            </button>
          </div>
        </div>

        {/* Reddit Spider */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🤖 Reddit Sentiment Tracker</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-600">Status:</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🟢 Running
                </span>
                <span className="text-sm text-gray-600">•</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  @task
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-4">Custom processing for Reddit posts and sentiment analysis</p>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
            <span>Target: reddit.com/r/investing</span>
            <span>•</span>
            <span>Created: 10 days ago</span>
            <span>•</span>
            <span>Last Run: 8 minutes ago</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Posts/Hour</p>
              <p className="font-semibold text-green-600">247</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="font-semibold text-green-600">94.1%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Processed</p>
              <p className="font-semibold">59,234 posts</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Runtime</p>
              <p className="font-semibold">10d 2h 45m</p>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 mb-2">Recent Activity:</p>
            <div className="space-y-1 text-sm text-gray-600">
              <p>• 8 min: Sentiment analysis batch completed</p>
              <p>• 25 min: High engagement post detected</p>
              <p>• 1 hr: Weekly trend report generated</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90">
              📊 View Data
            </button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              ⏸️ Pause
            </button>
            <Link href="/spiders/reddit-sentiment-tracker">
              <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
                ⚙️ Configure
              </button>
            </Link>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded text-sm hover:bg-secondary/80">
              📈 Analytics
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex items-center justify-center gap-4 mt-8 pt-6 border-t border-gray-200">
        <button className="px-4 py-2 text-primary hover:text-primary/80 font-medium">Load More Spiders...</button>
        <button className="px-4 py-2 text-muted-foreground hover:text-foreground font-medium">
          📈 Performance Report
        </button>
        <button className="px-4 py-2 text-muted-foreground hover:text-foreground font-medium">📋 Export List</button>
      </div>
    </div>
  )
}

export default function SpidersPage() {
  return (
    <DashboardLayout>
      <SpidersPageContent />
    </DashboardLayout>
  )
}
