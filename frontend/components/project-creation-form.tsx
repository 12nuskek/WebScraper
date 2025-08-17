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
import { Card, CardContent } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, Rocket, Plus, X } from "lucide-react"

interface ProjectCreationFormProps {
  onClose: () => void
}

export function ProjectCreationForm({ onClose }: ProjectCreationFormProps) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "",
    region: "",
    currency: "",
    template: "toy-market",
    tags: ["lego", "pricing", "australia", "retail"],
    launchOptions: {
      startImmediately: true,
      fullScan: true,
      smartAlerts: true,
      teamDashboard: true,
      welcomeEmail: false,
    },
  })

  const [newTag, setNewTag] = useState("")

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }))
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((tag) => tag !== tagToRemove),
    }))
  }

  const handleNext = () => {
    if (step < 2) setStep(step + 1)
  }

  const handleBack = () => {
    if (step > 1) setStep(step - 1)
  }

  const handleSubmit = () => {
    // Handle form submission
    console.log("Creating project:", formData)
    onClose()
  }

  if (step === 1) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🏗️</span>
            <h2 className="text-lg font-semibold">Create New Project</h2>
          </div>
          <Badge variant="secondary">Step 1 of 2</Badge>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Project Name</Label>
            <Input
              id="name"
              placeholder="LEGO Market Analysis"
              value={formData.name}
              onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Comprehensive LEGO pricing and sentiment analysis across Australian retailers"
              value={formData.description}
              onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
              rows={3}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, category: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="🧱 Toys & Games" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="toys">🧱 Toys & Games</SelectItem>
                  <SelectItem value="footwear">👟 Footwear</SelectItem>
                  <SelectItem value="wine">🍷 Wine & Spirits</SelectItem>
                  <SelectItem value="electronics">📱 Electronics</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Region</Label>
              <Select
                value={formData.region}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, region: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="🇦🇺 Australia" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="au">🇦🇺 Australia</SelectItem>
                  <SelectItem value="us">🇺🇸 United States</SelectItem>
                  <SelectItem value="uk">🇬🇧 United Kingdom</SelectItem>
                  <SelectItem value="ca">🇨🇦 Canada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Currency</Label>
              <Select
                value={formData.currency}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, currency: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="AUD - Australian Dollar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="aud">AUD - Australian Dollar</SelectItem>
                  <SelectItem value="usd">USD - US Dollar</SelectItem>
                  <SelectItem value="gbp">GBP - British Pound</SelectItem>
                  <SelectItem value="cad">CAD - Canadian Dollar</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-3">
            <Label>Project Template</Label>
            <p className="text-sm text-muted-foreground">Choose a template to get started faster</p>

            <RadioGroup
              value={formData.template}
              onValueChange={(value) => setFormData((prev) => ({ ...prev, template: value }))}
            >
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="scratch" id="scratch" />
                  <Label htmlFor="scratch">Start from scratch</Label>
                </div>

                <Card className="border-primary bg-primary/5">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <RadioGroupItem value="toy-market" id="toy-market" />
                      <Label htmlFor="toy-market" className="font-medium">
                        🧱 Toy Market Analysis Template
                      </Label>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-6">
                      <li>• Pre-configured for major toy retailers</li>
                      <li>• LEGO-specific data fields</li>
                      <li>• Sentiment analysis for forums</li>
                    </ul>
                  </CardContent>
                </Card>

                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="footwear" id="footwear" />
                  <Label htmlFor="footwear">👟 Footwear Intelligence Template</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="wine" id="wine" />
                  <Label htmlFor="wine">🍷 Wine Market Template</Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="gap-1">
                  #{tag}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 hover:bg-transparent"
                    onClick={() => removeTag(tag)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Add tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addTag()}
              />
              <Button variant="outline" size="sm" onClick={addTag}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={onClose}>
            <ChevronLeft className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          <Button onClick={handleNext}>
            Next: Review & Launch
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">🏗️</span>
          <h2 className="text-lg font-semibold">Create New Project - Review & Launch</h2>
        </div>
        <Badge variant="secondary">Step 2 of 2</Badge>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label>Project Summary</Label>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📋</span>
                <h3 className="font-medium">{formData.name || "LEGO Market Analysis"}</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Region: Australia | Currency: AUD | Category: Toys & Games
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-3">
          <Label>Launch Options</Label>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="start-immediately"
                checked={formData.launchOptions.startImmediately}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    launchOptions: { ...prev.launchOptions, startImmediately: !!checked },
                  }))
                }
              />
              <Label htmlFor="start-immediately">Start data collection immediately</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="full-scan"
                checked={formData.launchOptions.fullScan}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    launchOptions: { ...prev.launchOptions, fullScan: !!checked },
                  }))
                }
              />
              <Label htmlFor="full-scan">Run initial full catalog scan</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="smart-alerts"
                checked={formData.launchOptions.smartAlerts}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    launchOptions: { ...prev.launchOptions, smartAlerts: !!checked },
                  }))
                }
              />
              <Label htmlFor="smart-alerts">Enable smart monitoring alerts</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="team-dashboard"
                checked={formData.launchOptions.teamDashboard}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    launchOptions: { ...prev.launchOptions, teamDashboard: !!checked },
                  }))
                }
              />
              <Label htmlFor="team-dashboard">Create team dashboard</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="welcome-email"
                checked={formData.launchOptions.welcomeEmail}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    launchOptions: { ...prev.launchOptions, welcomeEmail: !!checked },
                  }))
                }
              />
              <Label htmlFor="welcome-email">Schedule welcome email to team members</Label>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={handleBack}>
          <ChevronLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex gap-2">
          <Button variant="outline">Save as Draft</Button>
          <Button onClick={handleSubmit} className="bg-primary">
            <Rocket className="h-4 w-4 mr-2" />
            Create & Launch Project
          </Button>
        </div>
      </div>
    </div>
  )
}
