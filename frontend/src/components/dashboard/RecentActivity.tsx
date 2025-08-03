import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

interface ActivityItem {
  id: string
  title: string
  description: string
  timestamp: string
  status: 'success' | 'error' | 'pending'
  type: string
}

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    title: 'E-commerce Spider',
    description: 'Successfully scraped 1,247 products',
    timestamp: '2 minutes ago',
    status: 'success',
    type: 'scrape'
  },
  {
    id: '2',
    title: 'News Website',
    description: 'Failed to extract article content',
    timestamp: '15 minutes ago',
    status: 'error',
    type: 'scrape'
  },
  {
    id: '3',
    title: 'Social Media Monitor',
    description: 'Collected 543 new posts',
    timestamp: '1 hour ago',
    status: 'success',
    type: 'monitor'
  },
  {
    id: '4',
    title: 'Data Export',
    description: 'Exporting scraped data to CSV',
    timestamp: '2 hours ago',
    status: 'pending',
    type: 'export'
  }
]

export default function RecentActivity() {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'success':
        return 'default'
      case 'error':
        return 'destructive'
      case 'pending':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockActivities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {activity.title}
                  </p>
                  <Badge variant={getStatusVariant(activity.status)}>
                    {activity.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {activity.description}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  {activity.timestamp}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}