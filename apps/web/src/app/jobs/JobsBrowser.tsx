/**
 * Jobs Browser — client component that reads URL search params
 * Must be wrapped in <Suspense> from its parent page
 */

"use client"

import { useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { FilterSidebar } from "@/components/jobs/FilterSidebar"
import { JobGrid } from "@/components/jobs/JobGrid"
import { Pagination } from "@/components/ui/Pagination"
import { useJobs, usePortals, useDomains } from "@/hooks/useJobs"
import { useSavedJobs } from "@/hooks/useSavedJobs"
import type { JobFilters } from "@/lib/types"
import { SORT_OPTIONS, PAGE_SIZE } from "@/lib/constants"
import { SlidersHorizontal, X } from "lucide-react"
import { Button } from "@/components/ui/button"

export function JobsBrowser() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { toggleSave, isSaved } = useSavedJobs()
  const [showMobileFilter, setShowMobileFilter] = useState(false)

  // Build initial filters from URL params
  const buildFiltersFromURL = (): JobFilters => {
    const filters: JobFilters = { page: 1, page_size: PAGE_SIZE }
    const q = searchParams.get("q")
    const domain = searchParams.get("domain")
    const skills = searchParams.get("skills")
    const seniority = searchParams.get("seniority")
    const portal = searchParams.get("portal")
    const is_remote = searchParams.get("is_remote")
    const is_fresher = searchParams.get("is_fresher")
    const sort = searchParams.get("sort")

    if (q) filters.skills = q
    if (domain) filters.domain = domain
    if (skills) filters.skills = skills
    if (seniority) filters.seniority = seniority
    if (portal) filters.portal = portal
    if (is_remote === "true") filters.is_remote = true
    if (is_fresher === "true") filters.is_fresher = true
    if (sort) {
      const [sort_by, sort_order] = sort.split(":")
      if (sort_by) filters.sort_by = sort_by
      if (sort_order) filters.sort_order = sort_order
    }

    return filters
  }

  const [filters, setFilters] = useState<JobFilters>(buildFiltersFromURL)
  const [sortValue, setSortValue] = useState(
    searchParams.get("sort") || "scraped_at:desc"
  )

  const { data: jobsData, isLoading, error } = useJobs(filters)
  const { data: portals = [] } = usePortals()
  const { data: domains = [] } = useDomains()

  const handleSortChange = (value: string) => {
    setSortValue(value)
    const [sort_by, sort_order] = value.split(":")
    setFilters(prev => ({ ...prev, sort_by, sort_order, page: 1 }))
  }

  const handleFiltersChange = (newFilters: JobFilters) => {
    setFilters(newFilters)
  }

  const handleClearAll = () => {
    const reset: JobFilters = {
      page: 1,
      page_size: PAGE_SIZE,
      sort_by: "scraped_at",
      sort_order: "desc",
    }
    setFilters(reset)
    setSortValue("scraped_at:desc")
    router.replace("/jobs")
  }

  const activeFilterCount = Object.keys(filters).filter((k) => {
    const key = k as keyof JobFilters
    const v = filters[key]
    return (
      v !== undefined &&
      v !== null &&
      v !== "" &&
      key !== "page" &&
      key !== "page_size" &&
      key !== "sort_by" &&
      key !== "sort_order"
    )
  }).length

  return (
    <div className="flex gap-6">
      {/* Desktop Filter Sidebar */}
      <aside className="hidden lg:block flex-shrink-0">
        <FilterSidebar
          filters={filters}
          onChange={handleFiltersChange}
          domains={domains}
          portals={portals}
          onClearAll={handleClearAll}
        />
      </aside>

      {/* Mobile Filter Overlay */}
      {showMobileFilter && (
        <FilterSidebar
          filters={filters}
          onChange={handleFiltersChange}
          domains={domains}
          portals={portals}
          onClearAll={handleClearAll}
          isMobile
          onClose={() => setShowMobileFilter(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 min-w-0 space-y-4">
        {/* Toolbar */}
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            {/* Mobile filter toggle */}
            <Button
              variant="outline"
              size="sm"
              className="lg:hidden flex items-center gap-2"
              onClick={() => setShowMobileFilter(true)}
            >
              <SlidersHorizontal className="h-4 w-4" />
              Filters
              {activeFilterCount > 0 && (
                <span className="ml-1 inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-primary text-primary-foreground rounded-full">
                  {activeFilterCount}
                </span>
              )}
            </Button>

            <p className="text-sm text-muted-foreground">
              {isLoading
                ? "Loading..."
                : jobsData
                ? `${jobsData.total.toLocaleString()} jobs found`
                : ""}
            </p>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <label htmlFor="sort-select" className="text-sm text-muted-foreground hidden sm:inline">
              Sort:
            </label>
            <select
              id="sort-select"
              value={sortValue}
              onChange={(e) => handleSortChange(e.target.value)}
              className="text-sm border rounded-md px-2 py-1.5 bg-background focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active filter chips */}
        {activeFilterCount > 0 && (
          <div className="flex flex-wrap gap-2">
            {filters.domain && (
              <FilterChip
                label={`Domain: ${filters.domain}`}
                onRemove={() => setFilters(prev => ({ ...prev, domain: undefined, page: 1 }))}
              />
            )}
            {filters.seniority && (
              <FilterChip
                label={`Seniority: ${filters.seniority}`}
                onRemove={() => setFilters(prev => ({ ...prev, seniority: undefined, page: 1 }))}
              />
            )}
            {filters.portal && (
              <FilterChip
                label={`Portal: ${filters.portal}`}
                onRemove={() => setFilters(prev => ({ ...prev, portal: undefined, page: 1 }))}
              />
            )}
            {filters.is_remote && (
              <FilterChip
                label="Remote"
                onRemove={() => setFilters(prev => ({ ...prev, is_remote: undefined, page: 1 }))}
              />
            )}
            {filters.is_fresher && (
              <FilterChip
                label="Fresher-friendly"
                onRemove={() => setFilters(prev => ({ ...prev, is_fresher: undefined, page: 1 }))}
              />
            )}
            {filters.skills && (
              <FilterChip
                label={`Skills: ${filters.skills}`}
                onRemove={() => setFilters(prev => ({ ...prev, skills: undefined, page: 1 }))}
              />
            )}
          </div>
        )}

        {/* Job Grid */}
        <JobGrid
          jobs={jobsData?.jobs}
          isLoading={isLoading}
          error={error?.message}
          onSaveJob={toggleSave}
          isSavedJob={isSaved}
        />

        {/* Pagination */}
        {jobsData && jobsData.total_pages > 1 && (
          <Pagination
            currentPage={jobsData.page}
            totalPages={jobsData.total_pages}
            onPageChange={(page) => setFilters(prev => ({ ...prev, page }))}
          />
        )}
      </div>
    </div>
  )
}

function FilterChip({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 bg-secondary text-secondary-foreground rounded-full text-xs font-medium">
      {label}
      <button onClick={onRemove} aria-label={`Remove ${label} filter`}>
        <X className="h-3 w-3" />
      </button>
    </span>
  )
}
