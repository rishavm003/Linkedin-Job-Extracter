/**
 * Job card component
 * Displays job information in a card format
 */

"use client"

import Link from "next/link"
import { Bookmark, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { DomainBadge } from "@/components/ui/DomainBadge"
import { PortalBadge } from "@/components/ui/PortalBadge"
import { SeniorityBadge } from "@/components/ui/SeniorityBadge"
import { SkillPill } from "@/components/ui/SkillPill"
import { useQueryClient } from "@tanstack/react-query"
import { fetchJobDetail } from "@/lib/api"
import { JobSummary } from "@/lib/types"
import { formatSalary, formatRelativeDate, truncateSkills } from "@/lib/utils"
import { MAX_SKILLS_DISPLAY } from "@/lib/constants"
import { cn } from "@/lib/utils"

interface JobCardProps {
  job: JobSummary
  onSave?: () => void
  isSaved?: boolean
  compact?: boolean
}

export function JobCard({ job, onSave, isSaved = false, compact = false }: JobCardProps) {
  const queryClient = useQueryClient()
  const { visible: visibleSkills, overflow: skillOverflow } = truncateSkills(job.skills, MAX_SKILLS_DISPLAY)

  const prefetchJob = () => {
    if (!job.id) return
    queryClient.prefetchQuery({
      queryKey: ["job", job.id],
      queryFn: () => fetchJobDetail(job.id),
      staleTime: 5 * 60 * 1000, // 5 minutes
    })
  }

  const handleSaveClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onSave?.()
  }

  const handleApplyClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    window.open(job.apply_url, "_blank", "noopener,noreferrer")
  }

  const cardContent = (
    <Card 
      onMouseEnter={prefetchJob}
      className={cn(
        "group relative h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] dark:hover:shadow-[0_8px_30px_rgb(255,255,255,0.02)] border-border/50 hover:border-primary/30 overflow-hidden bg-background/80 backdrop-blur-sm",
        compact ? "p-4" : "p-6"
      )}
    >
      {/* Decorative top gradient that fades in on hover */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary/40 to-indigo-500/40 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      {/* Header with badges */}
      <div className="flex justify-between items-start mb-3">
        <DomainBadge domain={job.domain} size="sm" />
        <PortalBadge portal={job.source_portal} displayName={job.portal_display_name} />
      </div>

      {/* Title and company */}
      <div className="mb-3 relative z-10">
        <h3 className={cn(
          "font-bold line-clamp-2 mb-1 group-hover:text-primary transition-colors duration-300",
          compact ? "text-base" : "text-lg"
        )}>
          {job.title}
        </h3>
        <p className="text-sm text-muted-foreground font-medium">
          {job.company} <span className="mx-1 opacity-50">•</span> {job.is_remote ? "Remote" : job.location}
        </p>
      </div>

      {/* Badges row */}
      <div className="flex flex-wrap gap-1 mb-3">
        <SeniorityBadge seniority={job.seniority} />
        {job.is_remote && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            Remote
          </span>
        )}
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
          {job.job_type}
        </span>
      </div>

      {/* Skills */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-1">
          {visibleSkills.map((skill) => (
            <SkillPill key={skill} skill={skill} />
          ))}
          {skillOverflow > 0 && (
            <span className="text-xs text-muted-foreground">
              +{skillOverflow} more
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-end">
        <div className="text-right">
          <div className={cn(
            "font-semibold",
            compact ? "text-sm" : "text-base"
          )}>
            {formatSalary(job.salary)}
          </div>
          <div className="text-xs text-muted-foreground">
            {formatRelativeDate(job.posted_at)}
          </div>
        </div>

        <div className="flex gap-2">
          {/* Save button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleSaveClick}
            className={cn(
              "p-2 transition-all duration-300", 
              isSaved ? "bg-primary/10 text-primary border-primary/20 hover:bg-primary/20" : "hover:text-primary hover:border-primary/30"
            )}
          >
            {isSaved ? (
              <Bookmark className="h-4 w-4 fill-current transition-transform duration-300 group-active:scale-90" />
            ) : (
              <Bookmark className="h-4 w-4 transition-transform duration-300 group-active:scale-90" />
            )}
          </Button>

          {/* Apply button */}
          <Button
            size="sm"
            onClick={handleApplyClick}
            className="flex items-center gap-1 transition-all duration-300 hover:shadow-md hover:shadow-primary/20 hover:-translate-y-0.5 active:scale-95"
          >
            Apply
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </Card>
  )

  if (compact) {
    return cardContent
  }

  return (
    <Link href={`/jobs/${job.id}`} className="block">
      {cardContent}
    </Link>
  )
}
