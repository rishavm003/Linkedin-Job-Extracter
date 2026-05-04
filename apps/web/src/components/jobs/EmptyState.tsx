/**
 * Empty state component
 * Shows when no data is available
 */

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface EmptyStateProps {
  title?: string
  description?: string
  action?: React.ReactNode
  icon?: React.ReactNode
  className?: string
}

export function EmptyState({ 
  title = "No jobs found", 
  description = "Try adjusting your filters or search query",
  action,
  icon,
  className 
}: EmptyStateProps) {
  // Default briefcase icon if none provided
  const defaultIcon = (
    <svg
      className="mx-auto h-12 w-12 text-muted-foreground"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
      />
    </svg>
  )

  return (
    <Card className={cn(
      "flex flex-col items-center justify-center p-8 text-center",
      className
    )}>
      {icon || defaultIcon}
      
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      
      <p className="mt-2 text-sm text-muted-foreground max-w-md">
        {description}
      </p>
      
      {action && (
        <div className="mt-6">
          {action}
        </div>
      )}
    </Card>
  )
}
