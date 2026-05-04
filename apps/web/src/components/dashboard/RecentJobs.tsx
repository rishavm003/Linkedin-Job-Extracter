/**
 * Recent jobs component for dashboard
 * Shows most recently added jobs
 */

import { JobCard } from "../jobs/JobCard"
import type { JobSummary } from "@/lib/types"

interface RecentJobsProps {
  jobs: JobSummary[]
  onSaveJob?: (id: string) => void
  isSavedJob?: (id: string) => boolean
}

export function RecentJobs({ jobs, onSaveJob, isSavedJob }: RecentJobsProps) {
  const recentJobs = jobs.slice(0, 4)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {recentJobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          compact={true}
          onSave={() => onSaveJob?.(job.id)}
          isSaved={isSavedJob?.(job.id)}
        />
      ))}
    </div>
  )
}
