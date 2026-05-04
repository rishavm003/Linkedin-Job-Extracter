/**
 * Dashboard page
 * Shows overview of job market with key metrics and charts
 */

"use client"

import { Briefcase, Users, Wifi, Globe } from "lucide-react"
import { SummaryCard } from "@/components/dashboard/SummaryCard"
import { RecentJobs } from "@/components/dashboard/RecentJobs"
import { DomainDonut } from "@/components/analytics/DomainDonut"
import { TopSkillsBar } from "@/components/analytics/TopSkillsBar"
import { RemoteDonut } from "@/components/analytics/RemoteDonut"
import { useAnalyticsDashboard } from "@/hooks/useAnalytics"
import { useJobs } from "@/hooks/useJobs"
import { useSavedJobs } from "@/hooks/useSavedJobs"
import { getGreeting } from "@/lib/utils"

export default function Dashboard() {
  const { data: analytics, isLoading: analyticsLoading } = useAnalyticsDashboard()
  const { data: jobsData, isLoading: jobsLoading } = useJobs({ 
    page_size: 8, 
    sort_by: "scraped_at", 
    sort_order: "desc" 
  })
  const { savedIds, toggleSave, isSaved } = useSavedJobs()

  if (analyticsLoading || jobsLoading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-muted rounded-lg animate-pulse" />
          <div className="h-64 bg-muted rounded-lg animate-pulse" />
        </div>
        <div className="h-96 bg-muted rounded-lg animate-pulse" />
        <div className="h-64 bg-muted rounded-lg animate-pulse" />
      </div>
    )
  }

  if (!analytics || !jobsData) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Failed to load dashboard data</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary/90 via-indigo-600/90 to-violet-800/90 p-8 sm:p-12 shadow-lg mb-8 text-white">
        <div className="absolute top-0 right-0 p-12 opacity-10 pointer-events-none">
          <Briefcase className="w-64 h-64 transform rotate-12 translate-x-16 -translate-y-8" />
        </div>
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 text-white">
            {getGreeting()}, 👋
          </h1>
          <p className="text-lg sm:text-xl text-primary-foreground/80 font-medium leading-relaxed">
            Here's what's happening in the job market today. 
            Discover the latest opportunities and track your applications.
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Total Jobs"
          value={analytics.summary.total_jobs}
          icon={Briefcase}
          color="primary"
        />
        <SummaryCard
          title="Fresher-Friendly"
          value={analytics.summary.fresher_friendly}
          icon={Users}
          color="success"
        />
        <SummaryCard
          title="Remote Jobs"
          value={analytics.summary.remote_jobs}
          icon={Wifi}
          color="warning"
        />
        <SummaryCard
          title="Portals Tracked"
          value={analytics.summary.portals_tracked}
          icon={Globe}
          color="primary"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DomainDonut data={analytics.domain_distribution} />
        <div className="space-y-6">
          <RemoteDonut data={analytics.remote_vs_onsite} />
          <div className="text-center p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              Domains covered: {analytics.summary.domains_covered}
            </p>
          </div>
        </div>
      </div>

      {/* Top Skills */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Top Skills in Demand</h2>
        <TopSkillsBar data={analytics.top_skills} limit={8} />
      </div>

      {/* Recent Jobs */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recently Added Jobs</h2>
          <a
            href="/jobs"
            className="text-sm text-primary hover:underline"
          >
            View all →
          </a>
        </div>
        <RecentJobs
          jobs={jobsData.jobs}
          onSaveJob={toggleSave}
          isSavedJob={isSaved}
        />
      </div>
    </div>
  )
}
