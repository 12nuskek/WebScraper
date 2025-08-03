import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { MoreHorizontal, Play, Pause, Settings } from "lucide-react"

interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'paused' | 'completed'
  lastRun: string
  itemsScraped: number
}

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'E-commerce Product Monitor',
    description: 'Track product prices and availability',
    status: 'active',
    lastRun: '2 hours ago',
    itemsScraped: 15420
  },
  {
    id: '2',
    name: 'News Aggregator',
    description: 'Collect latest news articles',
    status: 'active',
    lastRun: '30 minutes ago',
    itemsScraped: 8230
  },
  {
    id: '3',
    name: 'Social Media Tracker',
    description: 'Monitor social media mentions',
    status: 'paused',
    lastRun: '1 day ago',
    itemsScraped: 5670
  }
]

export default function ProjectOverview() {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'default'
      case 'paused':
        return 'secondary'
      case 'completed':
        return 'outline'
      default:
        return 'outline'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Active Projects</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockProjects.map((project) => (
            <div key={project.id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-medium text-gray-900">{project.name}</h3>
                    <Badge variant={getStatusVariant(project.status)}>
                      {project.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{project.description}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Last run: {project.lastRun}</span>
                    <span>Items: {project.itemsScraped.toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <Button variant="ghost" size="icon">
                    {project.status === 'active' ? (
                      <Pause className="h-4 w-4" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Settings className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}