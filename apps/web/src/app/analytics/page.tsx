/**
 * Analytics page
 * Shows comprehensive job market analytics and charts
 */

"use client"

import { DomainDonut } from "@/components/analytics/DomainDonut"
import { RemoteDonut } from "@/components/analytics/RemoteDonut"
import { TopSkillsBar } from "@/components/analytics/TopSkillsBar"
import { SeniorityChart } from "@/components/analytics/SeniorityChart"
import { PortalPie } from "@/components/analytics/PortalPie"
import { SalaryRangeChart } from "@/components/analytics/SalaryRangeChart"
import { TrendingSkills } from "@/components/analytics/TrendingSkills"
import { SummaryCard } from "@/components/dashboard/SummaryCard"
import { useAnalyticsDashboard, useTrendingSkills, useSalaryRanges } from "@/hooks/useAnalytics"
import { Briefcase, Users, Wifi, BarChart2 } from "lucide-react"

export default function AnalyticsPage() {
  const { data: analytics, isLoading: analyticsLoading } = useAnalyticsDashboard()
  const { data: trendingSkills, isLoading: trendingLoading } = useTrendingSkills()
  const { data: salaryRanges, isLoading: salaryLoading } = useSalaryRanges()

  if (analyticsLoading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-64 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Failed to load analytics data</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
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
          title="Domains Covered"
          value={analytics.summary.domains_covered}
          icon={BarChart2}
          color="primary"
        />
      </div>

      {/* Domain & Remote Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Domain Distribution</h2>
          <DomainDonut data={analytics.domain_distribution} />
        </div>
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Seniority Breakdown</h2>
          <SeniorityChart data={analytics.seniority_breakdown} />
        </div>
      </div>

      {/* Portal & Remote */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Portal Distribution</h2>
          <PortalPie data={analytics.portal_distribution} />
        </div>
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Remote vs On-site</h2>
          <RemoteDonut data={analytics.remote_vs_onsite} />
        </div>
      </div>

      {/* Top Skills */}
      <div className="bg-card border rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Top Skills in Demand</h2>
        <TopSkillsBar data={analytics.top_skills} limit={15} />
      </div>

      {/* Trending Skills */}
      {!trendingLoading && trendingSkills && trendingSkills.length > 0 && (
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Trending Skills This Week</h2>
          <TrendingSkills data={trendingSkills} />
        </div>
      )}

      {/* Salary Ranges */}
      {!salaryLoading && salaryRanges && salaryRanges.length > 0 && (
        <div className="bg-card border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Average Salary by Domain (LPA)</h2>
          <SalaryRangeChart data={salaryRanges} />
        </div>
      )}
    </div>
  )
}
