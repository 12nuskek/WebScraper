"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import {
  ArrowLeft,
  ArrowRight,
  X,
  Plus,
  Globe,
  Zap,
  Settings,
  CheckCircle,
  AlertTriangle,
  Info,
  Sparkles,
} from "lucide-react"

interface SpiderCreationFormProps {
  onClose: () => void
}

interface FormData {
  // Step 1: Basic Information
  spiderName: string
  description: string
  spiderType: string
  targetUrl: string
  category: string
  project: string
  priority: string
  dataScope: string
  specificUrls: string
  tags: string[]
  enableSitemap: boolean
  sitemapUrl: string
  sitemapAutoDetect: boolean

  // Step 2: Decorator Selection
  decorator: string

  // Step 3: Browser Configuration
  headless: boolean
  blockImages: boolean
  blockImagesAndCss: boolean
  waitForCompletePageLoad: boolean
  userAgent: string
  windowSize: string
  profile: string
  tinyProfile: boolean
  lang: string
  proxy: string
  chromeArguments: string[]
  extensions: string[]
  capsolverApiKey: string
  parallel: number
  reuseDriver: boolean
  cache: boolean
  maxRetry: number
  retryWait: number
  closeOnCrash: boolean
  raiseException: boolean
  createErrorLogs: boolean
  output: string
  outputFormats: string[]

  // Step 4: Request Configuration (for @request)
  requestsPerMinute: number
  delayBetweenRequests: number
  respectRobotsTxt: boolean

  // Step 5: Task Configuration (for @task)
  taskParallel: number
  taskCache: boolean
  taskMaxRetry: number
  processingConfig: string
}

export function SpiderCreationForm({ onClose }: SpiderCreationFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<FormData>({
    spiderName: "BigW LEGO Scraper",
    description: "Monitor LEGO product pricing and availability from BigW Australia retail website",
    spiderType: "e-commerce",
    targetUrl: "https://www.bigw.com.au",
    category: "toys-games",
    project: "lego-market-analysis",
    priority: "high",
    dataScope: "category",
    specificUrls: "",
    tags: ["bigw", "retail", "lego", "australia"],
    enableSitemap: true,
    sitemapUrl: "https://www.bigw.com.au/sitemap.xml",
    sitemapAutoDetect: true,
    decorator: "browser",
    headless: true,
    blockImages: true,
    blockImagesAndCss: false,
    waitForCompletePageLoad: true,
    userAgent: "hashed",
    windowSize: "hashed",
    profile: "bigw_spider_profile",
    tinyProfile: true,
    lang: "english",
    proxy: "http://user:pass@proxy.com:8080",
    chromeArguments: ["--disable-web-security", "--no-sandbox"],
    extensions: ["adblock", "capsolver"],
    capsolverApiKey: "CAP-1234567890abcdef",
    parallel: 3,
    reuseDriver: true,
    cache: true,
    maxRetry: 3,
    retryWait: 10,
    closeOnCrash: true,
    raiseException: false,
    createErrorLogs: true,
    output: "bigw_products",
    outputFormats: ["json", "excel"],
    requestsPerMinute: 60,
    delayBetweenRequests: 1,
    respectRobotsTxt: true,
    taskParallel: 5,
    taskCache: true,
    taskMaxRetry: 3,
    processingConfig: "",
  })

  const [newTag, setNewTag] = useState("")

  const steps = [
    { number: 1, title: "Define Your Spider", description: "Basic information and target configuration" },
    { number: 2, title: "Choose Method", description: "Select the best scraping approach" },
    { number: 3, title: "Configure Settings", description: "Fine-tune performance and behavior" },
    { number: 4, title: "Advanced Options", description: "Error handling and optimization" },
    { number: 5, title: "Review & Deploy", description: "Final review and deployment options" },
  ]

  const addTag = () => {
    if (newTag && !formData.tags.includes(newTag)) {
      setFormData((prev) => ({ ...prev, tags: [...prev.tags, newTag] }))
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData((prev) => ({ ...prev, tags: prev.tags.filter((tag) => tag !== tagToRemove) }))
  }

  const nextStep = () => setCurrentStep((prev) => Math.min(prev + 1, 5))
  const prevStep = () => setCurrentStep((prev) => Math.max(prev - 1, 1))

  const handleSubmit = () => {
    console.log("Spider configuration:", formData)
    onClose()
  }

  const renderStep1 = () => (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold">Define Your Spider</h3>
        <p className="text-muted-foreground">Let's start with the basics - what do you want to scrape?</p>
      </div>

      <Card className="border-2 hover:border-primary/20 transition-colors">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="h-5 w-5 text-primary" />
            Spider Identity
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="spiderName" className="text-sm font-medium">
                Spider Name
              </Label>
              <Input
                id="spiderName"
                value={formData.spiderName}
                onChange={(e) => setFormData((prev) => ({ ...prev, spiderName: e.target.value }))}
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="spiderType" className="text-sm font-medium">
                Spider Type
              </Label>
              <Select
                value={formData.spiderType}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, spiderType: value }))}
              >
                <SelectTrigger className="h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="e-commerce">🛒 E-commerce Site</SelectItem>
                  <SelectItem value="news">📰 News & Media</SelectItem>
                  <SelectItem value="social">👥 Social Media</SelectItem>
                  <SelectItem value="api">🔌 API Endpoint</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium">
              Description
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="resize-none"
              placeholder="Describe what this spider will do and what data it will collect..."
            />
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 hover:border-primary/20 transition-colors">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Globe className="h-5 w-5 text-primary" />
            Target Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="targetUrl" className="text-sm font-medium">
                Target URL
              </Label>
              <Input
                id="targetUrl"
                value={formData.targetUrl}
                onChange={(e) => setFormData((prev) => ({ ...prev, targetUrl: e.target.value }))}
                className="h-11"
                placeholder="https://example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="category" className="text-sm font-medium">
                Category
              </Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, category: value }))}
              >
                <SelectTrigger className="h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="toys-games">🧱 Toys & Games</SelectItem>
                  <SelectItem value="electronics">📱 Electronics</SelectItem>
                  <SelectItem value="fashion">👕 Fashion</SelectItem>
                  <SelectItem value="home-garden">🏠 Home & Garden</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="project" className="text-sm font-medium">
                Project Assignment
              </Label>
              <Select
                value={formData.project}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, project: value }))}
              >
                <SelectTrigger className="h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="lego-market-analysis">LEGO Market Analysis</SelectItem>
                  <SelectItem value="sneaker-intelligence">Sneaker Intelligence</SelectItem>
                  <SelectItem value="wine-tracker">Wine Investment Tracker</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority" className="text-sm font-medium">
                Priority
              </Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, priority: value }))}
              >
                <SelectTrigger className="h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="high">🔥 High</SelectItem>
                  <SelectItem value="medium">⚡ Medium</SelectItem>
                  <SelectItem value="low">📋 Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-dashed border-primary/30 bg-primary/5 hover:border-primary/50 transition-colors">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Globe className="h-5 w-5 text-primary" />
            Sitemap Analysis
            <Badge variant="secondary" className="ml-auto">
              Recommended
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-3">
            <Checkbox
              id="enableSitemap"
              checked={formData.enableSitemap}
              onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, enableSitemap: !!checked }))}
              className="h-5 w-5"
            />
            <Label htmlFor="enableSitemap" className="text-sm font-medium">
              Enable sitemap analysis
            </Label>
          </div>

          <div className="bg-background/50 rounded-lg p-4 border">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div className="space-y-1">
                <p className="text-sm font-medium">Smart URL Discovery</p>
                <p className="text-sm text-muted-foreground">
                  The spider will first analyze the sitemap to identify product URLs and build transformation patterns.
                  This helps optimize data extraction and ensures comprehensive coverage.
                </p>
              </div>
            </div>
          </div>

          {formData.enableSitemap && (
            <div className="space-y-4 pl-8 border-l-2 border-primary/20">
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="sitemapAutoDetect"
                  checked={formData.sitemapAutoDetect}
                  onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, sitemapAutoDetect: !!checked }))}
                  className="h-4 w-4"
                />
                <Label htmlFor="sitemapAutoDetect" className="text-sm">
                  Auto-detect sitemap URL
                </Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="sitemapUrl" className="text-sm font-medium">
                  Sitemap URL
                </Label>
                <Input
                  id="sitemapUrl"
                  value={formData.sitemapUrl}
                  onChange={(e) => setFormData((prev) => ({ ...prev, sitemapUrl: e.target.value }))}
                  placeholder="https://example.com/sitemap.xml"
                  disabled={formData.sitemapAutoDetect}
                  className="h-10"
                />
                {formData.sitemapAutoDetect && (
                  <p className="text-xs text-muted-foreground">
                    Will automatically check: /sitemap.xml, /sitemap_index.xml, /robots.txt
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-2 hover:border-primary/20 transition-colors">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Data Scope</CardTitle>
          </CardHeader>
          <CardContent>
            <RadioGroup
              value={formData.dataScope}
              onValueChange={(value) => setFormData((prev) => ({ ...prev, dataScope: value }))}
              className="space-y-3"
            >
              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                <RadioGroupItem value="full" id="full" />
                <Label htmlFor="full" className="flex-1 cursor-pointer">
                  Full catalog scan
                </Label>
              </div>
              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                <RadioGroupItem value="category" id="category" />
                <Label htmlFor="category" className="flex-1 cursor-pointer">
                  Product category: LEGO products only
                </Label>
              </div>
              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                <RadioGroupItem value="specific" id="specific" />
                <Label htmlFor="specific" className="flex-1 cursor-pointer">
                  Specific URLs
                </Label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>

        <Card className="border-2 hover:border-primary/20 transition-colors">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Tags</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="gap-1 px-3 py-1">
                  #{tag}
                  <X className="h-3 w-3 cursor-pointer hover:text-destructive" onClick={() => removeTag(tag)} />
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Add tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addTag()}
                className="h-10"
              />
              <Button type="button" variant="outline" size="sm" onClick={addTag} className="px-3 bg-transparent">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold">Choose Your Method</h3>
        <p className="text-muted-foreground">Select the best approach for your scraping needs</p>
      </div>

      <RadioGroup
        value={formData.decorator}
        onValueChange={(value) => setFormData((prev) => ({ ...prev, decorator: value }))}
        className="space-y-4"
      >
        <Card
          className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
            formData.decorator === "browser"
              ? "ring-2 ring-primary shadow-lg border-primary/50 bg-primary/5"
              : "border-2 hover:border-primary/30"
          }`}
          onClick={() => setFormData((prev) => ({ ...prev, decorator: "browser" }))}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="browser" id="browser" className="h-5 w-5" />
              <Globe className="h-6 w-6 text-primary" />
              <div className="flex-1">
                <CardTitle className="text-xl">@browser - Full Browser Automation</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">Complete browser control with JavaScript execution</p>
              </div>
              {formData.decorator === "browser" && <CheckCircle className="h-5 w-5 text-primary" />}
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  JavaScript execution & dynamic content
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Anti-bot detection handling
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Perfect for SPAs and complex sites
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  Higher resource usage
                </div>
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  Slower than HTTP requests
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
            formData.decorator === "request"
              ? "ring-2 ring-primary shadow-lg border-primary/50 bg-primary/5"
              : "border-2 hover:border-primary/30"
          }`}
          onClick={() => setFormData((prev) => ({ ...prev, decorator: "request" }))}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="request" id="request" className="h-5 w-5" />
              <Zap className="h-6 w-6 text-primary" />
              <div className="flex-1">
                <CardTitle className="text-xl">@request - Lightning Fast HTTP</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">High-speed HTTP requests with smart headers</p>
              </div>
              {formData.decorator === "request" && <CheckCircle className="h-5 w-5 text-primary" />}
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Ultra-fast performance
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Low resource consumption
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Perfect for APIs and simple sites
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  No JavaScript execution
                </div>
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  Limited anti-bot capabilities
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
            formData.decorator === "task"
              ? "ring-2 ring-primary shadow-lg border-primary/50 bg-primary/5"
              : "border-2 hover:border-primary/30"
          }`}
          onClick={() => setFormData((prev) => ({ ...prev, decorator: "task" }))}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="task" id="task" className="h-5 w-5" />
              <Settings className="h-6 w-6 text-primary" />
              <div className="flex-1">
                <CardTitle className="text-xl">@task - Custom Processing</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">Maximum flexibility for complex workflows</p>
              </div>
              {formData.decorator === "task" && <CheckCircle className="h-5 w-5 text-primary" />}
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Complete customization
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  External library integration
                </div>
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  Perfect for ML and data processing
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  Requires custom implementation
                </div>
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  More complex setup
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </RadioGroup>
    </div>
  )

  // ... existing code for renderStep3, renderStep4, renderStep5 ...
  const renderStep3 = () => {
    if (formData.decorator === "browser") {
      return (
        <div className="space-y-8">
          <div className="text-center space-y-2">
            <h3 className="text-2xl font-bold">Configure Browser Settings</h3>
            <p className="text-muted-foreground">Fine-tune your browser automation for optimal performance</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-2 hover:border-primary/20 transition-colors">
              <CardHeader>
                <CardTitle className="text-lg">Basic Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 gap-6">
                  <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <Checkbox
                      id="headless"
                      checked={formData.headless}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, headless: !!checked }))}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="headless" className="text-sm">
                      Headless mode
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <Checkbox
                      id="blockImages"
                      checked={formData.blockImages}
                      onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, blockImages: !!checked }))}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="blockImages" className="text-sm">
                      Block images
                    </Label>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="userAgent" className="text-sm font-medium">
                      User Agent
                    </Label>
                    <Select
                      value={formData.userAgent}
                      onValueChange={(value) => setFormData((prev) => ({ ...prev, userAgent: value }))}
                    >
                      <SelectTrigger className="h-10">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hashed">UserAgent.HASHED (recommended)</SelectItem>
                        <SelectItem value="random">UserAgent.RANDOM</SelectItem>
                        <SelectItem value="custom">Custom string</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="windowSize" className="text-sm font-medium">
                      Window Size
                    </Label>
                    <Select
                      value={formData.windowSize}
                      onValueChange={(value) => setFormData((prev) => ({ ...prev, windowSize: value }))}
                    >
                      <SelectTrigger className="h-10">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hashed">WindowSize.HASHED</SelectItem>
                        <SelectItem value="random">WindowSize.RANDOM</SelectItem>
                        <SelectItem value="1920x1080">1920x1080</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/20 transition-colors">
              <CardHeader>
                <CardTitle className="text-lg">Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="profile" className="text-sm font-medium">
                      Profile Name
                    </Label>
                    <Input
                      id="profile"
                      value={formData.profile}
                      onChange={(e) => setFormData((prev) => ({ ...prev, profile: e.target.value }))}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="parallel" className="text-sm font-medium">
                      Parallel Instances
                    </Label>
                    <Input
                      id="parallel"
                      type="number"
                      value={formData.parallel}
                      onChange={(e) => setFormData((prev) => ({ ...prev, parallel: Number.parseInt(e.target.value) }))}
                      className="h-10"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Proxy & Output</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="proxy" className="text-sm font-medium">
                  Proxy URL
                </Label>
                <Input
                  id="proxy"
                  value={formData.proxy}
                  onChange={(e) => setFormData((prev) => ({ ...prev, proxy: e.target.value }))}
                  placeholder="http://user:pass@proxy.com:8080"
                  className="h-10"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="output" className="text-sm font-medium">
                    Output Filename
                  </Label>
                  <Input
                    id="output"
                    value={formData.output}
                    onChange={(e) => setFormData((prev) => ({ ...prev, output: e.target.value }))}
                    className="h-10"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Output Formats</Label>
                  <div className="flex gap-4 mt-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="json"
                        checked={formData.outputFormats.includes("json")}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setFormData((prev) => ({ ...prev, outputFormats: [...prev.outputFormats, "json"] }))
                          } else {
                            setFormData((prev) => ({
                              ...prev,
                              outputFormats: prev.outputFormats.filter((f) => f !== "json"),
                            }))
                          }
                        }}
                      />
                      <Label htmlFor="json" className="text-sm">
                        JSON
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="excel"
                        checked={formData.outputFormats.includes("excel")}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setFormData((prev) => ({ ...prev, outputFormats: [...prev.outputFormats, "excel"] }))
                          } else {
                            setFormData((prev) => ({
                              ...prev,
                              outputFormats: prev.outputFormats.filter((f) => f !== "excel"),
                            }))
                          }
                        }}
                      />
                      <Label htmlFor="excel" className="text-sm">
                        Excel
                      </Label>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    if (formData.decorator === "request") {
      return (
        <div className="space-y-8">
          <div className="text-center space-y-2">
            <h3 className="text-2xl font-bold">Configure HTTP Settings</h3>
            <p className="text-muted-foreground">Optimize your HTTP requests for speed and reliability</p>
          </div>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Request Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="requestParallel" className="text-sm font-medium">
                    Parallel Requests
                  </Label>
                  <Input
                    id="requestParallel"
                    type="number"
                    value={40}
                    onChange={(e) => setFormData((prev) => ({ ...prev, parallel: Number.parseInt(e.target.value) }))}
                    className="h-10"
                  />
                  <p className="text-xs text-muted-foreground">HTTP requests can handle higher parallelism</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="requestsPerMinute" className="text-sm font-medium">
                    Requests per Minute
                  </Label>
                  <Input
                    id="requestsPerMinute"
                    type="number"
                    value={formData.requestsPerMinute}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, requestsPerMinute: Number.parseInt(e.target.value) }))
                    }
                    className="h-10"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                <Checkbox
                  id="respectRobots"
                  checked={formData.respectRobotsTxt}
                  onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, respectRobotsTxt: !!checked }))}
                  className="h-4 w-4"
                />
                <Label htmlFor="respectRobots" className="text-sm">
                  Respect robots.txt
                </Label>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    if (formData.decorator === "task") {
      return (
        <div className="space-y-8">
          <div className="text-center space-y-2">
            <h3 className="text-2xl font-bold">Configure Task Processing</h3>
            <p className="text-muted-foreground">Set up your custom processing workflow</p>
          </div>

          <Card className="border-2 hover:border-primary/20 transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Processing Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="taskParallel" className="text-sm font-medium">
                    Parallel Workers
                  </Label>
                  <Input
                    id="taskParallel"
                    type="number"
                    value={formData.taskParallel}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, taskParallel: Number.parseInt(e.target.value) }))
                    }
                    className="h-10"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="taskMaxRetry" className="text-sm font-medium">
                    Max Retries
                  </Label>
                  <Input
                    id="taskMaxRetry"
                    type="number"
                    value={formData.taskMaxRetry}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, taskMaxRetry: Number.parseInt(e.target.value) }))
                    }
                    className="h-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="processingConfig" className="text-sm font-medium">
                  Processing Configuration
                </Label>
                <Textarea
                  id="processingConfig"
                  value={formData.processingConfig}
                  onChange={(e) => setFormData((prev) => ({ ...prev, processingConfig: e.target.value }))}
                  placeholder="Custom processing logic, ML models, API integrations..."
                  rows={6}
                  className="resize-none"
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return null
  }

  const renderStep4 = () => (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold">Advanced Options</h3>
        <p className="text-muted-foreground">Configure error handling and optimization settings</p>
      </div>

      <Card className="border-2 hover:border-primary/20 transition-colors">
        <CardHeader>
          <CardTitle className="text-lg">Error Handling & Recovery</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="maxRetry" className="text-sm font-medium">
                Max Retry Attempts
              </Label>
              <Input
                id="maxRetry"
                type="number"
                value={formData.maxRetry}
                onChange={(e) => setFormData((prev) => ({ ...prev, maxRetry: Number.parseInt(e.target.value) }))}
                className="h-10"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="retryWait" className="text-sm font-medium">
                Retry Wait (seconds)
              </Label>
              <Input
                id="retryWait"
                type="number"
                value={formData.retryWait}
                onChange={(e) => setFormData((prev) => ({ ...prev, retryWait: Number.parseInt(e.target.value) }))}
                className="h-10"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox
                id="closeOnCrash"
                checked={formData.closeOnCrash}
                onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, closeOnCrash: !!checked }))}
                className="h-4 w-4"
              />
              <Label htmlFor="closeOnCrash" className="text-sm">
                Close on crash
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox
                id="createErrorLogs"
                checked={formData.createErrorLogs}
                onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, createErrorLogs: !!checked }))}
                className="h-4 w-4"
              />
              <Label htmlFor="createErrorLogs" className="text-sm">
                Error logging
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox
                id="cache"
                checked={formData.cache}
                onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, cache: !!checked }))}
                className="h-4 w-4"
              />
              <Label htmlFor="cache" className="text-sm">
                Result caching
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderStep5 = () => (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold">Review & Deploy</h3>
        <p className="text-muted-foreground">Final review of your spider configuration</p>
      </div>

      <Card className="border-2 border-primary/30 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-primary" />
            Spider Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="font-medium">Name:</span>
                <span className="text-muted-foreground">{formData.spiderName}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Type:</span>
                <span className="text-muted-foreground">{formData.spiderType}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Target:</span>
                <span className="text-muted-foreground truncate">{formData.targetUrl}</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="font-medium">Method:</span>
                <span className="text-muted-foreground">@{formData.decorator}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Project:</span>
                <span className="text-muted-foreground">{formData.project}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Priority:</span>
                <span className="text-muted-foreground">{formData.priority}</span>
              </div>
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <span className="font-medium">Description:</span>
            <p className="text-sm text-muted-foreground bg-background/50 p-3 rounded-lg">{formData.description}</p>
          </div>

          <div className="space-y-2">
            <span className="font-medium">Tags:</span>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="px-3 py-1">
                  #{tag}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 hover:border-primary/20 transition-colors">
        <CardHeader>
          <CardTitle className="text-lg">Deployment Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox id="deployNow" defaultChecked className="h-4 w-4" />
              <Label htmlFor="deployNow" className="text-sm">
                Deploy immediately
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox id="testRun" defaultChecked className="h-4 w-4" />
              <Label htmlFor="testRun" className="text-sm">
                Run test with 10 URLs
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox id="monitoring" defaultChecked className="h-4 w-4" />
              <Label htmlFor="monitoring" className="text-sm">
                Enable monitoring
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
              <Checkbox id="schedule" className="h-4 w-4" />
              <Label htmlFor="schedule" className="text-sm">
                Automated scheduling
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const currentStepData = steps[currentStep - 1]
  const progress = (currentStep / 5) * 100

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold">Create New Spider</h2>
          <p className="text-muted-foreground">
            Step {currentStep} of 5 • {currentStepData.title}
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="h-10 w-10 p-0">
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="mb-8 space-y-4">
        <div className="relative">
          <Progress value={progress} className="h-2" />
          <div className="absolute inset-0 flex items-center justify-between px-1">
            {steps.map((step) => (
              <div
                key={step.number}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-200 ${
                  step.number <= currentStep
                    ? "bg-primary text-primary-foreground border-primary shadow-lg"
                    : "bg-background text-muted-foreground border-border"
                }`}
              >
                {step.number <= currentStep ? (
                  step.number < currentStep ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    step.number
                  )
                ) : (
                  step.number
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-5 gap-2 text-xs">
          {steps.map((step) => (
            <div key={step.number} className="text-center space-y-1">
              <div className={`font-medium ${step.number === currentStep ? "text-primary" : "text-muted-foreground"}`}>
                {step.title}
              </div>
              <div className="text-muted-foreground text-xs leading-tight">{step.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="min-h-[600px] mb-8">
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
        {currentStep === 5 && renderStep5()}
      </div>

      <div className="flex justify-between items-center pt-6 border-t">
        <Button variant="outline" onClick={prevStep} disabled={currentStep === 1} className="h-11 px-6 bg-transparent">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        <div className="text-sm text-muted-foreground">
          {currentStep} of {steps.length} steps completed
        </div>

        {currentStep < 5 ? (
          <Button onClick={nextStep} className="h-11 px-6">
            Next: {steps[currentStep]?.title}
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} className="h-11 px-6 bg-green-600 hover:bg-green-700">
            <CheckCircle className="h-4 w-4 mr-2" />
            Deploy Spider
          </Button>
        )}
      </div>
    </div>
  )
}
