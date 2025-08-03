import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { BarChart3 } from "lucide-react"

interface ChartPlaceholderProps {
  title: string
  description?: string
  height?: number
}

export default function ChartPlaceholder({ 
  title, 
  description = "Chart data will be displayed here",
  height = 300 
}: ChartPlaceholderProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && (
          <p className="text-sm text-gray-600">{description}</p>
        )}
      </CardHeader>
      <CardContent>
        <div 
          className="flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
          style={{ height: `${height}px` }}
        >
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-sm">Chart placeholder</p>
            <p className="text-gray-400 text-xs mt-1">Connect to data source to display charts</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}