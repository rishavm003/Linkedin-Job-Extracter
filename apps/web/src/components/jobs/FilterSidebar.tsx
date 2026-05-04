/**
 * Filter sidebar component
 * Provides filtering options for job listings
 */

"use client"

import { useState } from "react"
import { Button, buttonVariants } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronUp, X } from "lucide-react"
import type { JobFilters, DomainInfo, PortalInfo } from "@/lib/types"
import { SENIORITY_LEVELS, JOB_TYPES } from "@/lib/constants"
import { cn } from "@/lib/utils"

interface FilterSidebarProps {
  filters: JobFilters
  onChange: (filters: JobFilters) => void
  domains: DomainInfo[]
  portals: PortalInfo[]
  onClearAll: () => void
  isMobile?: boolean
  onClose?: () => void
}

export function FilterSidebar({ 
  filters, 
  onChange, 
  domains, 
  portals, 
  onClearAll,
  isMobile = false,
  onClose
}: FilterSidebarProps) {
  const [expandedSections, setExpandedSections] = useState({
    quick: true,
    domain: true,
    seniority: true,
    jobType: false,
    portal: false,
    salary: false,
    sort: false,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const updateFilter = (key: keyof JobFilters, value: any) => {
    onChange({
      ...filters,
      [key]: value,
      page: 1, // Reset page when filter changes
    })
  }

  const hasActiveFilters = Object.keys(filters).some(key => {
    const value = filters[key as keyof JobFilters]
    return value !== undefined && value !== null && value !== "" && key !== "page" && key !== "page_size"
  })

  const CollapsibleSection = ({ 
    title, 
    section, 
    children, 
    badge 
  }: { 
    title: string
    section: keyof typeof expandedSections
    children: React.ReactNode
    badge?: number
  }) => (
    <Collapsible
      open={expandedSections[section]}
      onOpenChange={() => toggleSection(section)}
    >
      <CollapsibleTrigger 
        className={cn(buttonVariants({ variant: "ghost" }), "w-full justify-between p-3 h-auto")}
      >
        <span className="font-medium">{title}</span>
        <div className="flex items-center gap-2">
          {badge && (
            <Badge variant="secondary" className="text-xs">
              {badge}
            </Badge>
          )}
          {expandedSections[section] ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className="px-3 pb-3">
        {children}
      </CollapsibleContent>
    </Collapsible>
  )

  return (
    <div className={cn(
      "space-y-4",
      isMobile && "fixed inset-0 z-50 bg-background p-4 overflow-y-auto",
      !isMobile && "w-80"
    )}>
      {isMobile && (
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Filters</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Quick Filters */}
      <Card>
        <CollapsibleSection title="Quick Filters" section="quick">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="fresher"
                checked={filters.is_fresher || false}
                onCheckedChange={(checked) => updateFilter("is_fresher", checked)}
              />
              <Label htmlFor="fresher" className="text-sm">
                Fresher-friendly only
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="remote"
                checked={filters.is_remote || false}
                onCheckedChange={(checked) => updateFilter("is_remote", checked)}
              />
              <Label htmlFor="remote" className="text-sm">
                Remote only
              </Label>
            </div>
          </div>
        </CollapsibleSection>
      </Card>

      {/* Domain Filter */}
      <Card>
        <CollapsibleSection title="Domain" section="domain" badge={domains.length}>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {domains.map((domain) => (
              <div key={domain.domain} className="flex items-center space-x-2">
                <Checkbox
                  id={domain.domain}
                  checked={filters.domain === domain.domain}
                  onCheckedChange={(checked) => 
                    updateFilter("domain", checked ? domain.domain : undefined)
                  }
                />
                <Label htmlFor={domain.domain} className="text-sm flex-1">
                  {domain.domain}
                </Label>
                <Badge variant="outline" className="text-xs">
                  {domain.count}
                </Badge>
              </div>
            ))}
          </div>
          {filters.domain && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => updateFilter("domain", undefined)}
              className="mt-2 text-xs"
            >
              Clear
            </Button>
          )}
        </CollapsibleSection>
      </Card>

      {/* Seniority Filter */}
      <Card>
        <CollapsibleSection title="Seniority" section="seniority">
          <RadioGroup
            value={filters.seniority || ""}
            onValueChange={(value) => updateFilter("seniority", value || undefined)}
          >
            {SENIORITY_LEVELS.map((level) => (
              <div key={level.value} className="flex items-center space-x-2">
                <RadioGroupItem value={level.value} id={level.value} />
                <Label htmlFor={level.value} className="text-sm">
                  {level.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </CollapsibleSection>
      </Card>

      {/* Job Type Filter */}
      <Card>
        <CollapsibleSection title="Job Type" section="jobType">
          <div className="space-y-2">
            {JOB_TYPES.map((type) => (
              <div key={type} className="flex items-center space-x-2">
                <Checkbox
                  id={type}
                  checked={filters.job_type === type}
                  onCheckedChange={(checked) => 
                    updateFilter("job_type", checked ? type : undefined)
                  }
                />
                <Label htmlFor={type} className="text-sm">
                  {type}
                </Label>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      </Card>

      {/* Portal Filter */}
      <Card>
        <CollapsibleSection title="Portal" section="portal" badge={portals.length}>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {portals
              .sort((a, b) => b.count - a.count)
              .map((portal) => (
                <div key={portal.portal} className="flex items-center space-x-2">
                  <Checkbox
                    id={portal.portal}
                    checked={filters.portal === portal.portal}
                    onCheckedChange={(checked) => 
                      updateFilter("portal", checked ? portal.portal : undefined)
                    }
                  />
                  <Label htmlFor={portal.portal} className="text-sm flex-1">
                    {portal.display_name}
                  </Label>
                  <Badge variant="outline" className="text-xs">
                    {portal.count}
                  </Badge>
                </div>
              ))}
          </div>
        </CollapsibleSection>
      </Card>

      {/* Salary Range Filter */}
      <Card>
        <CollapsibleSection title="Salary Range" section="salary">
          <div className="space-y-4">
            <div className="px-2">
              <Slider
                value={[
                  filters.salary_min ? filters.salary_min / 100000 : 0,
                  filters.salary_max ? filters.salary_max / 100000 : 20
                ]}
                onValueChange={(value) => {
                  const values = Array.isArray(value) ? value : [value]
                  onChange({
                    ...filters,
                    salary_min: values[0] * 100000,
                    salary_max: values[1] * 100000,
                    page: 1,
                  })
                }}
                max={20}
                min={0}
                step={1}
                className="w-full"
              />
            </div>
            <div className="text-center text-sm text-muted-foreground">
              ₹{filters.salary_min ? Math.round(filters.salary_min / 100000) : 0} LPA — {" "}
              ₹{filters.salary_max ? Math.round(filters.salary_max / 100000) : 20} LPA
            </div>
          </div>
        </CollapsibleSection>
      </Card>

      {/* Clear All Button */}
      {hasActiveFilters && (
        <Button
          variant="outline"
          onClick={onClearAll}
          className="w-full"
        >
          Clear all filters
        </Button>
      )}
    </div>
  )
}
