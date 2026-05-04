/**
 * Saved Jobs page
 * Shows all jobs saved by the user (stored in localStorage)
 */

"use client"

import { useJobs } from "@/hooks/useJobs"
import { useSavedJobs } from "@/hooks/useSavedJobs"
import { JobCard } from "@/components/jobs/JobCard"
import { EmptyState } from "@/components/jobs/EmptyState"
import { Bookmark, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function SavedJobsPage() {
  const { savedIds, isSaved, toggleSave, clearAll } = useSavedJobs()

  // Fetch all jobs and filter by saved IDs
  const { data: jobsData, isLoading } = useJobs({ page_size: 100 })

  const savedJobs = jobsData?.jobs.filter((job) => savedIds.includes(job.id)) ?? []

  if (savedIds.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <EmptyState
          title="No saved jobs yet"
          description="Browse jobs and click the bookmark icon to save them here for later."
          icon={
            <Bookmark className="mx-auto h-12 w-12 text-muted-foreground" />
          }
          action={
            <a
              href="/jobs"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Browse Jobs
            </a>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          {savedIds.length} job{savedIds.length !== 1 ? "s" : ""} saved
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={clearAll}
          className="flex items-center gap-2 text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
          Clear all
        </Button>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: savedIds.length > 4 ? 4 : savedIds.length }).map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      )}

      {/* Saved job grid */}
      {!isLoading && savedJobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {savedJobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onSave={() => toggleSave(job.id)}
              isSaved={isSaved(job.id)}
            />
          ))}
        </div>
      )}

      {/* IDs saved but none matched the current page's jobs (edge case) */}
      {!isLoading && savedJobs.length === 0 && savedIds.length > 0 && (
        <EmptyState
          title="Saved jobs not found"
          description="Some saved jobs may have been removed. Try clearing your saved list."
        />
      )}
    </div>
  )
}
