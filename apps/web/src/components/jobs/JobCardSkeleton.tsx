/**
 * Job card skeleton component
 * Loading placeholder for JobCard
 */

import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

interface JobCardSkeletonProps {
  compact?: boolean
}

export function JobCardSkeleton({ compact = false }: JobCardSkeletonProps) {
  return (
    <Card className={cn(
      "h-full",
      compact ? "p-4" : "p-6"
    )}>
      {/* Header with badges */}
      <div className="flex justify-between items-start mb-3">
        <Skeleton className="h-5 w-20 rounded-full" />
        <Skeleton className="h-5 w-16 rounded-md" />
      </div>

      {/* Title and company */}
      <div className="mb-3">
        <Skeleton className={cn(
          "h-5 w-full mb-2",
          compact ? "h-4" : "h-6"
        )} />
        <Skeleton className="h-4 w-32" />
      </div>

      {/* Badges row */}
      <div className="flex flex-wrap gap-1 mb-3">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-12 rounded-full" />
        <Skeleton className="h-5 w-20 rounded-full" />
      </div>

      {/* Skills */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-1">
          <Skeleton className="h-6 w-12 rounded-full" />
          <Skeleton className="h-6 w-16 rounded-full" />
          <Skeleton className="h-6 w-14 rounded-full" />
          <Skeleton className="h-6 w-10 rounded-full" />
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-end">
        <div className="text-right">
          <Skeleton className={cn(
            "h-5 w-20 mb-1",
            compact ? "h-4 w-16" : "h-5 w-24"
          )} />
          <Skeleton className="h-3 w-16" />
        </div>

        <div className="flex gap-2">
          <Skeleton className="h-8 w-8 rounded" />
          <Skeleton className="h-8 w-16 rounded" />
        </div>
      </div>
    </Card>
  )
}
