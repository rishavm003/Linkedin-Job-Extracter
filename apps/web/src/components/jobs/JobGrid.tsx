/**
 * Job grid component
 * Displays jobs in a responsive grid layout
 */

import { JobCard } from "./JobCard"
import { JobCardSkeleton } from "./JobCardSkeleton"
import { EmptyState } from "./EmptyState"
import { JobSummary } from "@/lib/types"
import { cn } from "@/lib/utils"

interface JobGridProps {
  jobs: JobSummary[] | undefined
  isLoading: boolean
  error?: string
  onSaveJob?: (id: string) => void
  isSavedJob?: (id: string) => boolean
  compact?: boolean
  className?: string
}

export function JobGrid({ 
  jobs, 
  isLoading, 
  error, 
  onSaveJob, 
  isSavedJob,
  compact = false,
  className 
}: JobGridProps) {
  if (isLoading) {
    return (
      <div className={cn(
        "grid gap-4",
        compact 
          ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" 
          : "grid-cols-1 md:grid-cols-2"
      , className)}>
        {Array.from({ length: 6 }).map((_, index) => (
          <JobCardSkeleton key={index} compact={compact} />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <EmptyState
        title="Failed to load jobs"
        description="Check if the API is running and try again."
        action={
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        }
      />
    )
  }

  if (!jobs || jobs.length === 0) {
    return (
      <EmptyState
        title="No jobs match your filters"
        description="Try adjusting your filters or search query"
        action={
          <button
            onClick={() => window.location.href = "/jobs"}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Clear all filters
          </button>
        }
      />
    )
  }

  return (
    <div className={cn(
      "grid gap-4",
      compact 
        ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" 
        : "grid-cols-1 md:grid-cols-2"
    , className)}>
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          onSave={() => onSaveJob?.(job.id)}
          isSaved={isSavedJob?.(job.id)}
          compact={compact}
        />
      ))}
    </div>
  )
}
