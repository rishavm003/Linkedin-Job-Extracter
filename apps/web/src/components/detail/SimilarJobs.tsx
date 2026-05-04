/**
 * Similar jobs component
 * Shows related job recommendations
 */

import { JobCard } from "../jobs/JobCard"
import type { JobSummary } from "@/lib/types"

interface SimilarJobsProps {
  jobs: JobSummary[]
  onSaveJob?: (id: string) => void
  isSavedJob?: (id: string) => boolean
}

export function SimilarJobs({ jobs, onSaveJob, isSavedJob }: SimilarJobsProps) {
  if (!jobs || jobs.length === 0) {
    return null
  }

  return (
    <section className="mt-12">
      <h2 className="text-2xl font-semibold mb-6">Similar jobs you might like</h2>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {jobs.slice(0, 4).map((job) => (
          <div
            key={job.id}
            className="flex-none w-[280px]"
          >
            <JobCard
              job={job}
              compact={true}
              onSave={() => onSaveJob?.(job.id)}
              isSaved={isSavedJob?.(job.id)}
            />
          </div>
        ))}
      </div>
    </section>
  )
}
