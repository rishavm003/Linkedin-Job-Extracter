/**
 * Job detail header component
 * Shows job title, company, and key information
 */

import { Button } from "@/components/ui/button"
import { DomainBadge } from "@/components/ui/DomainBadge"
import { PortalBadge } from "@/components/ui/PortalBadge"
import { SeniorityBadge } from "@/components/ui/SeniorityBadge"
import { JobDetail } from "@/lib/types"
import { formatSalary, formatAbsoluteDate } from "@/lib/utils"
import { Bookmark, ExternalLink } from "lucide-react"

interface JobDetailHeaderProps {
  job: JobDetail
  onSave?: () => void
  isSaved?: boolean
}

export function JobDetailHeader({ job, onSave, isSaved = false }: JobDetailHeaderProps) {
  const handleApplyClick = () => {
    window.open(job.apply_url, "_blank", "noopener,noreferrer")
  }

  const handleSaveClick = () => {
    onSave?.()
  }

  return (
    <div className="space-y-6">
      {/* Title and Company */}
      <div>
        <h1 className="text-3xl font-bold mb-2">{job.title}</h1>
        <h2 className="text-xl text-muted-foreground mb-1">{job.company}</h2>
        <p className="text-muted-foreground">
          {job.is_remote ? "Remote" : job.location}
        </p>
      </div>

      {/* Badges Row */}
      <div className="flex flex-wrap gap-2">
        <DomainBadge domain={job.domain} />
        <SeniorityBadge seniority={job.seniority} />
        <PortalBadge portal={job.source_portal} displayName={job.portal_display_name} />
        {job.is_remote && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            Remote
          </span>
        )}
      </div>

      {/* Posted Date */}
      <div className="text-sm text-muted-foreground">
        Posted {formatAbsoluteDate(job.posted_at)}
        {job.posted_at !== job.scraped_at && (
          <span className="ml-2">
            • Scraped {formatAbsoluteDate(job.scraped_at)}
          </span>
        )}
      </div>

      {/* Salary */}
      <div className="text-2xl font-bold">
        {formatSalary(job.salary)}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Button
          onClick={handleApplyClick}
          className="flex-1 sm:flex-none"
        >
          Apply Now
          <ExternalLink className="ml-2 h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          onClick={handleSaveClick}
          className="flex-1 sm:flex-none"
        >
          {isSaved ? (
            <>
              <Bookmark className="mr-2 h-4 w-4 fill-current" />
              Saved
            </>
          ) : (
            <>
              <Bookmark className="mr-2 h-4 w-4" />
              Save Job
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
