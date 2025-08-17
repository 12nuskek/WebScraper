import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import {
  ArrowLeft,
  Settings,
  Users,
  Bell,
  Edit3,
  Copy,
  Trash2,
  Download,
  CheckCircle,
  AlertTriangle,
  Clock,
  RotateCcw,
  TestTube,
  Rocket,
  Save,
  RefreshCw,
  FileText,
  HelpCircle,
  GraduationCap,
  Calendar,
  BarChart3,
  TrendingUp,
  Zap,
} from "lucide-react"
import Link from "next/link"

export default function SpiderDetailPage({ params }: { params: { id: string } }) {
  const category = "exampleCategory"
  const subcategory = "exampleSubcategory"
  const product = "exampleProduct"
  const sku = "exampleSKU"

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/spiders">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">🕷️ Spider Configuration: BigW LEGO Australia</h1>
              <p className="text-muted-foreground">Botasaurus v1.2.3 • Created 2 minutes ago by Sarah Chen</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <BarChart3 className="h-4 w-4 mr-2" />
              Dashboard
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm">
              <Users className="h-4 w-4 mr-2" />
              Team
            </Button>
            <Button variant="outline" size="sm">
              <Bell className="h-4 w-4 mr-2" />
              <Badge variant="secondary" className="ml-1">
                3
              </Badge>
            </Button>
          </div>
        </div>

        {/* Spider Overview */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  🟡 DISCOVERY PHASE IN PROGRESS
                </Badge>
                <CardTitle>📋 Spider Overview</CardTitle>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Edit3 className="h-4 w-4 mr-2" />
                  Edit Details
                </Button>
                <Button variant="outline" size="sm">
                  <Copy className="h-4 w-4 mr-2" />
                  Clone
                </Button>
                <Button variant="outline" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export Config
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Spider Name</Label>
                <p className="text-sm">BigW LEGO Australia</p>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Target URL</Label>
                <p className="text-sm text-primary">https://www.bigw.com.au/c/toys/lego</p>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Framework</Label>
                <p className="text-sm">Botasaurus v1.2.3</p>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Created</Label>
                <p className="text-sm">2 minutes ago by Sarah Chen</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Discovery Phase */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">🔍 Discovery Phase</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                  📊 AUTOMATED DISCOVERY IN PROGRESS
                </Badge>
                <span className="text-sm text-muted-foreground">73%</span>
              </div>
              <Progress value={73} className="h-2" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Started: 2 min ago</span>
                <span>ETA: 1 min</span>
                <span>Analyzing site structure</span>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🤖 robots.txt Analysis</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">robots.txt discovered</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Crawl delays parsed</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Restrictions identified</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>📋 Rules: 2-3 sec delays</div>
                <div>🚫 Blocked: /admin/*, /api/internal/*</div>
              </div>
              <div className="p-3 bg-blue-50 rounded text-sm">
                💡 Recommendation: Respect 3-second delays between requests
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🗺️ Sitemap Discovery</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">sitemap.xml</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">products.xml</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">categories.xml</span>
                </div>
                <div className="flex items-center gap-2">
                  <RotateCcw className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">mobile.xml</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-sm">images.xml</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-sm">brands.xml</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>📦 Product URLs Found: 847 LEGO products</div>
                <div>
                  📁 Category Patterns: /c/{category}/{subcategory}
                </div>
              </div>
              <div className="text-sm">
                🏷️ Product Patterns: /p/{product}-{sku}/
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🔌 API Discovery</h4>
              <div className="p-4 border rounded space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Network Request Monitoring</span>
                  <Badge variant="outline">Auto-Detecting</Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div>🔍 Monitoring AJAX calls...</div>
                  <div>⚠️ API Endpoints Found: /api/products/search</div>
                  <div>🔒 Authentication: Required (session-based)</div>
                  <div>❌ Direct API Access: Not accessible - falling back to HTML</div>
                </div>
                <div className="p-3 bg-blue-50 rounded text-sm">
                  💡 Proceeding with HTML scraping via Botasaurus @request
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Phase */}
        <Card>
          <CardHeader>
            <CardTitle>📊 Analysis Phase</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">🔬 Page Structure Analysis</h4>
                <Badge variant="outline">Botasaurus Mode</Badge>
              </div>
              <div className="space-y-3">
                {[
                  { field: "Product Name", selector: 'h1[data-testid="product-title"]', confidence: 98 },
                  { field: "Price (AUD)", selector: ".price-current span", confidence: 95 },
                  { field: "SKU", selector: '[data-testid="product-code"]', confidence: 99 },
                  { field: "Availability", selector: ".stock-indicator span", confidence: 92 },
                  { field: "Rating", selector: ".rating-stars [aria-label]", confidence: 87 },
                  { field: "Reviews", selector: ".review-count", confidence: 78 },
                  { field: "Images", selector: ".product-images img[src]", confidence: 94 },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center gap-3">
                      {item.confidence >= 90 ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      )}
                      <div>
                        <p className="font-medium text-sm">{item.field}</p>
                        <p className="text-xs text-muted-foreground">{item.selector}</p>
                      </div>
                    </div>
                    <Badge variant={item.confidence >= 90 ? "default" : "secondary"}>{item.confidence}%</Badge>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <TestTube className="h-4 w-4 mr-2" />
                  Test Selectors
                </Button>
                <Button variant="outline" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Re-analyze
                </Button>
                <Button variant="outline" size="sm">
                  <Edit3 className="h-4 w-4 mr-2" />
                  Custom Selectors
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🛡️ Protection & JavaScript Detection</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">CloudFlare:</span>
                      <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                        🟡 Basic protection detected
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Bot Detection:</span>
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        🟢 None found
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">JavaScript:</span>
                      <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                        🟡 Required for lazy loading
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Rate Limiting:</span>
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        ✅ 10 requests/minute limit
                      </Badge>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <h5 className="font-medium text-sm">🤖 Botasaurus Strategy:</h5>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li>• @request for static content (90% of pages)</li>
                      <li>• @browser for JS-heavy product galleries</li>
                      <li>• Human-like delays (3-5 seconds)</li>
                      <li>• Caching system for efficiency</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Evasion Settings
                  </Button>
                  <Button variant="outline" size="sm">
                    <TestTube className="h-4 w-4 mr-2" />
                    Test Protection
                  </Button>
                  <Button variant="outline" size="sm">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Success Rate
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Botasaurus Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>⚙️ Botasaurus Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">🔧 Scraper Setup</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium">Primary Method</Label>
                      <div className="flex gap-4 mt-2">
                        <label className="flex items-center gap-2">
                          <input type="radio" name="method" defaultChecked />
                          <span className="text-sm">@request + caching</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="radio" name="method" />
                          <span className="text-sm">@browser</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="radio" name="method" />
                          <span className="text-sm">Hybrid</span>
                        </label>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm">Concurrency</Label>
                        <div className="flex items-center gap-2 mt-1">
                          <Input type="number" defaultValue="1" className="w-16" />
                          <span className="text-sm">session</span>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm">Max Pages</Label>
                        <Input type="number" defaultValue="50" className="w-20 mt-1" />
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium">Rate Control</Label>
                      <div className="space-y-2 mt-2">
                        <div className="flex items-center gap-2">
                          <Label className="text-sm">Request delay:</Label>
                          <Input defaultValue="3-5" className="w-20" />
                          <span className="text-sm">seconds</span>
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">Random delays</Label>
                          </div>
                          <div className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">Mouse movements</Label>
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground">Retry logic: 3 attempts with backoff</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <FileText className="h-4 w-4 mr-2" />
                    Component Details
                  </Button>
                  <Button variant="outline" size="sm">
                    <Zap className="h-4 w-4 mr-2" />
                    Performance Test
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Advanced
                  </Button>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">📥 Data Pipeline</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="space-y-2">
                  <div className="text-sm">1. Sitemap URLs → bt.sitemap utility</div>
                  <div className="text-sm">2. HTML Extraction → @request with bt.cache</div>
                  <div className="text-sm">3. Data Processing → @task for cleaning/validation</div>
                  <div className="text-sm">4. Edge Cases → @browser fallback</div>
                  <div className="text-sm">5. Export → bt utilities (CSV, JSON, Excel)</div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-sm mb-2">Error Handling:</h5>
                    <div className="space-y-1">
                      {["Automatic retries", "Fallback strategies", "Data validation"].map((option, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Switch defaultChecked />
                          <Label className="text-sm">{option}</Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h5 className="font-medium text-sm mb-2">Quality Control:</h5>
                    <div className="space-y-1">
                      {["Duplicate detection", "Quality monitoring", "Real-time alerts"].map((option, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Switch defaultChecked />
                          <Label className="text-sm">{option}</Label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Pipeline Status
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure Steps
                  </Button>
                  <Button variant="outline" size="sm">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Monitor
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Testing & Validation */}
        <Card>
          <CardHeader>
            <CardTitle>🧪 Testing & Validation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">🎯 Pre-Flight Validation</h4>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { check: "robots.txt compliance", status: "success" },
                  { check: "Sitemap accessible", status: "success" },
                  { check: "Selectors validated", status: "success" },
                  { check: "Protection bypassed", status: "success" },
                  { check: "Botasaurus configured", status: "success" },
                  { check: "JS pages need @browser", status: "warning" },
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    {item.status === "success" ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    )}
                    <span className="text-sm">{item.check}</span>
                  </div>
                ))}
              </div>
              <div className="p-3 bg-blue-50 rounded">
                <div className="text-sm font-medium mb-1">Test Configuration:</div>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Sample: 10 products across categories</li>
                  <li>• Methods: @request primary, @browser fallback</li>
                  <li>• Success target: 95%+ data completeness</li>
                </ul>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🚀 Test Execution</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm">Sample Size</Label>
                      <Input type="number" defaultValue="10" className="mt-1" />
                    </div>
                    <div>
                      <Label className="text-sm">Test Categories</Label>
                      <div className="space-y-2 mt-2">
                        {["Creator", "City", "Friends"].map((cat, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{cat}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm">Components</Label>
                      <div className="space-y-2 mt-2">
                        {["@request", "@browser", "@task"].map((comp, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{comp}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm">Validation</Label>
                      <div className="space-y-2 mt-2">
                        {["Selector accuracy", "Data completeness"].map((val, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{val}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 bg-green-50 rounded">
                  <div className="text-sm font-medium mb-1">Expected Results:</div>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 95%+ success with @request</li>
                    <li>• &lt;5% requiring @browser fallback</li>
                    <li>• Cache hit rate: 90%+</li>
                  </ul>
                </div>
                <div className="flex gap-2">
                  <Button>
                    <Rocket className="h-4 w-4 mr-2" />
                    Run Test
                  </Button>
                  <Button variant="outline">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Validate
                  </Button>
                  <Button variant="outline">
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Optimize
                  </Button>
                  <Button variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    Report
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Production Deployment */}
        <Card>
          <CardHeader>
            <CardTitle>📅 Production Deployment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">⚙️ Optimization Configuration</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium">Monitoring</Label>
                      <div className="space-y-2 mt-2">
                        {["Success rates", "Response times"].map((option, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{option}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Auto-adjustment</Label>
                      <div className="space-y-2 mt-2">
                        {["Delay tuning", "Concurrency scaling"].map((option, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{option}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium">Cache Strategy</Label>
                      <div className="space-y-2 mt-2">
                        {["Smart refresh", "Selective invalidation"].map((option, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{option}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Edge Case Handling</Label>
                      <ul className="text-sm space-y-1 text-muted-foreground mt-2">
                        <li>• Lazy-loaded images → @browser trigger</li>
                        <li>• AJAX pagination → Scroll simulation</li>
                        <li>• Dynamic pricing → Real-time updates</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Performance Dashboard
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Auto-Tune
                  </Button>
                  <Button variant="outline" size="sm">
                    <Bell className="h-4 w-4 mr-2" />
                    Alerts
                  </Button>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">📈 Monitoring & Scheduling</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium">Full Crawl</Label>
                      <div className="flex gap-4 mt-2">
                        <label className="flex items-center gap-2">
                          <input type="radio" name="fullcrawl" />
                          <span className="text-sm">Daily</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="radio" name="fullcrawl" defaultChecked />
                          <span className="text-sm">Weekly</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="radio" name="fullcrawl" />
                          <span className="text-sm">Custom</span>
                        </label>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm">Delta Updates</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input defaultValue="Every 30 min" className="w-32" />
                        <span className="text-sm">for price/stock changes</span>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm">Active Hours</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input defaultValue="09:00" className="w-20" />
                        <span className="text-sm">to</span>
                        <Input defaultValue="21:00" className="w-20" />
                        <span className="text-sm">AEST</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium">Smart Triggers</Label>
                      <div className="space-y-2 mt-2">
                        {[
                          "Price change detection",
                          "New product alerts",
                          "Stock level monitoring",
                          "Rating fluctuations",
                        ].map((trigger, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Switch defaultChecked />
                            <Label className="text-sm">{trigger}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Botasaurus Features</Label>
                      <ul className="text-sm space-y-1 text-muted-foreground mt-2">
                        <li>• Cache-first strategy for unchanged pages</li>
                        <li>• Incremental updates using URL patterns</li>
                        <li>• Automatic retry with exponential backoff</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Calendar className="h-4 w-4 mr-2" />
                    Schedule
                  </Button>
                  <Button variant="outline" size="sm">
                    <Zap className="h-4 w-4 mr-2" />
                    Triggers
                  </Button>
                  <Button variant="outline" size="sm">
                    <Bell className="h-4 w-4 mr-2" />
                    Alerts
                  </Button>
                  <Button variant="outline" size="sm">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Analytics
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Deployment Ready */}
        <Card>
          <CardHeader>
            <CardTitle>🎯 Deployment Ready</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">📊 Expected Performance (Botasaurus Optimized)</h4>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Products Monitored:</span>
                    <span className="text-sm font-medium">847 LEGO items</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Daily Data Points:</span>
                    <span className="text-sm font-medium">~40,656 (price, stock, ratings)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Success Rate:</span>
                    <span className="text-sm font-medium">&gt;97% (@request + @browser fallback)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Full Crawl Time:</span>
                    <span className="text-sm font-medium">25 minutes (with caching)</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Cache Hit Rate:</span>
                    <span className="text-sm font-medium">90%+ (unchanged product pages)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Storage/Month:</span>
                    <span className="text-sm font-medium">300 MB (compressed with bt utilities)</span>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Resource Usage:</Label>
                    <ul className="text-sm space-y-1 text-muted-foreground mt-1">
                      <li>• @request calls: ~760 pages (90%)</li>
                      <li>• @browser calls: ~87 pages (10% JS-heavy)</li>
                      <li>• Cache efficiency: 90% hit rate</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Detailed Metrics
                </Button>
                <Button variant="outline" size="sm">
                  Cost Estimate
                </Button>
                <Button variant="outline" size="sm">
                  <Zap className="h-4 w-4 mr-2" />
                  Optimize
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🎯 Action Center</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="font-medium">Ready for Production Deployment</span>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Discovery phase complete</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Botasaurus configured</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Protection handling ready</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Cache strategy optimized</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Error handling robust</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm">Awaiting final test</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Deployment Pipeline:</Label>
                  <ol className="text-sm space-y-1 text-muted-foreground">
                    <li>1. Final validation test (10 products)</li>
                    <li>2. Production spider deployment</li>
                    <li>3. Monitor first 100 pages</li>
                    <li>4. Full-scale crawl activation</li>
                  </ol>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <Button>
                    <TestTube className="h-4 w-4 mr-2" />
                    Final Test
                  </Button>
                  <Button>
                    <Rocket className="h-4 w-4 mr-2" />
                    Deploy Spider
                  </Button>
                  <Button variant="outline">
                    <Save className="h-4 w-4 mr-2" />
                    Save Config
                  </Button>
                  <Button variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    Review Setup
                  </Button>
                  <Button variant="outline">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Monitor Launch
                  </Button>
                  <Button variant="outline">
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Rollback Plan
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Technical Architecture */}
        <Card>
          <CardHeader>
            <CardTitle>🔧 Technical Architecture</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">🏗️ Botasaurus Component Map</h4>
              <div className="p-4 border rounded space-y-4">
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-sm">Discovery Phase:</span>
                    <ul className="text-sm space-y-1 text-muted-foreground mt-1 ml-4">
                      <li>├── bt.sitemap() → URL extraction & pattern analysis</li>
                      <li>├── robots.txt parser → Crawl delay compliance</li>
                      <li>└── Network monitor → API discovery & fallback</li>
                    </ul>
                  </div>
                  <div>
                    <span className="font-medium text-sm">Extraction Phase:</span>
                    <ul className="text-sm space-y-1 text-muted-foreground mt-1 ml-4">
                      <li>├── @request (primary) → Fast HTML scraping with caching</li>
                      <li>├── @browser (fallback) → JS-heavy pages & lazy loading</li>
                      <li>├── @task → Data processing & validation pipeline</li>
                      <li>└── bt.cache → Intelligent caching system</li>
                    </ul>
                  </div>
                  <div>
                    <span className="font-medium text-sm">Output Phase:</span>
                    <ul className="text-sm space-y-1 text-muted-foreground mt-1 ml-4">
                      <li>├── bt utilities → Multi-format export (CSV, JSON, Excel)</li>
                      <li>├── Data validation → Quality checks & duplicate detection</li>
                      <li>└── Real-time monitoring → Success rates & alerts</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">🔄 Workflow Integration</h4>
              <div className="p-4 border rounded space-y-4">
                <div>
                  <Label className="text-sm font-medium">🎯 Next Steps</Label>
                  <ol className="text-sm space-y-1 text-muted-foreground mt-2">
                    <li>1. Run comprehensive test crawl (all components)</li>
                    <li>2. Validate Botasaurus performance metrics</li>
                    <li>3. Deploy with monitoring & auto-optimization</li>
                    <li>4. Scale based on success rates & efficiency</li>
                  </ol>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <FileText className="h-4 w-4 mr-2" />
                    Botasaurus Docs
                  </Button>
                  <Button variant="outline" size="sm">
                    <HelpCircle className="h-4 w-4 mr-2" />
                    Technical Support
                  </Button>
                  <Button variant="outline" size="sm">
                    <GraduationCap className="h-4 w-4 mr-2" />
                    Best Practices
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
