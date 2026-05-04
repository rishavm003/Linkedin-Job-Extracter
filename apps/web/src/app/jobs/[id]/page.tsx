/**
 * Job detail page
 * Shows full job details with apply/save actions and similar jobs
 */

"use client"

import { use } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { JobDetailHeader } from "@/components/detail/JobDetailHeader"
import { JobDetailBody } from "@/components/detail/JobDetailBody"
import { SimilarJobs } from "@/components/detail/SimilarJobs"
import { useJobDetail } from "@/hooks/useJobs"
import { useSavedJobs } from "@/hooks/useSavedJobs"

interface JobDetailPageProps {
  params: Promise<{ id: string }>
}

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const { id } = use(params)
  const { data: job, isLoading, error } = useJobDetail(id)
  const { isSaved, toggleSave } = useSavedJobs()

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Back button skeleton */}
        <div className="h-8 w-32 bg-muted rounded animate-pulse" />
        {/* Header skeleton */}
        <div className="space-y-3">
          <div className="h-8 w-3/4 bg-muted rounded animate-pulse" />
          <div className="h-6 w-1/2 bg-muted rounded animate-pulse" />
          <div className="h-6 w-1/3 bg-muted rounded animate-pulse" />
          <div className="flex gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-6 w-20 bg-muted rounded-full animate-pulse" />
            ))}
          </div>
          <div className="flex gap-3 mt-4">
            <div className="h-10 w-28 bg-muted rounded animate-pulse" />
            <div className="h-10 w-28 bg-muted rounded animate-pulse" />
          </div>
        </div>
        {/* Body skeleton */}
        <div className="space-y-3 mt-8">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-4 bg-muted rounded animate-pulse" style={{ width: `${70 + Math.random() * 30}%` }} />
          ))}
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-muted-foreground">
          {error ? "Failed to load job details." : "Job not found."}
        </p>
        <Link
          href="/jobs"
          className="mt-4 inline-flex items-center gap-2 text-primary hover:underline"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Jobs
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back navigation */}
      <Link
        href="/jobs"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to jobs
      </Link>

      {/* Job header */}
      <JobDetailHeader
        job={job}
        onSave={() => toggleSave(job.id)}
        isSaved={isSaved(job.id)}
      />

      {/* Divider */}
      <div className="my-8 border-t" />

      {/* Job body */}
      <JobDetailBody job={job} />

      {/* Similar jobs */}
      {job.similar_jobs && job.similar_jobs.length > 0 && (
        <SimilarJobs
          jobs={job.similar_jobs}
          onSaveJob={toggleSave}
          isSavedJob={isSaved}
        />
      )}
    </div>
  )
}
