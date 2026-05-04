/**
 * TypeScript interfaces for JobExtractor API responses
 * These types exactly match the FastAPI backend schemas
 */

export interface Salary {
  min_value: number | null
  max_value: number | null
  currency: string | null
  period: string | null
  is_disclosed: boolean
  raw: string | null
}

export interface JobSummary {
  id: string
  title: string
  company: string
  location: string
  is_remote: boolean
  source_portal: string
  portal_display_name: string
  apply_url: string
  job_type: string
  seniority: string
  domain: string
  skills: string[]
  salary: Salary
  posted_at: string | null
  scraped_at: string
  description_summary: string
  is_fresher_friendly: boolean
  requires_experience: string | null
}

export interface JobDetail extends JobSummary {
  qualifications: string[]
  soft_skills: string[]
  description_clean: string
  country: string | null
  city: string | null
  fingerprint: string
  similar_jobs: JobSummary[]
}

export interface JobListResponse {
  jobs: JobSummary[]
  total: number
  page: number
  page_size: number
  total_pages: number
  source: string
}

export interface JobSearchResponse {
  jobs: JobSummary[]
  total: number
  query: string
  source: string
}

export interface JobFilters {
  domain?: string
  seniority?: string
  is_remote?: boolean
  portal?: string
  is_fresher?: boolean
  skills?: string
  salary_min?: number
  salary_max?: number
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: string
  job_type?: string
}

export interface AnalyticsSummary {
  total_jobs: number
  fresher_friendly: number
  remote_jobs: number
  portals_tracked: number
  domains_covered: number
  last_scraped_at: string | null
}

export interface DomainDistribution {
  domain: string
  count: number
  percentage: number
}

export interface SkillInfo {
  skill: string
  count: number
}

export interface SeniorityBreakdown {
  seniority: string
  count: number
  percentage: number
}

export interface PortalDistribution {
  portal: string
  display_name: string
  count: number
  percentage: number
}

export interface RemoteVsOnsite {
  remote: number
  onsite: number
  remote_percentage: number
}

export interface TrendingSkill {
  skill: string
  count_this_week: number
  count_last_week: number
  change_pct: number
}

export interface SalaryRange {
  domain: string
  avg_min: number | null
  avg_max: number | null
  currency: string
}

export interface AnalyticsDashboard {
  summary: AnalyticsSummary
  domain_distribution: DomainDistribution[]
  top_skills: SkillInfo[]
  seniority_breakdown: SeniorityBreakdown[]
  portal_distribution: PortalDistribution[]
  remote_vs_onsite: RemoteVsOnsite
  source: string
}

// Additional types for API responses
export interface PortalInfo {
  portal: string
  display_name: string
  count: number
}

export interface DomainInfo {
  domain: string
  count: number
}

export interface HealthResponse {
  status: string
  postgres: string
  elasticsearch: string
  redis: string
  jobs_in_db: number
  version: string
}

// AI Assistant types
export interface AIStatus {
  ollama_available: boolean
  model: string
  ollama_url: string
  setup_instructions?: string
}

export interface AIQueryRequest {
  question: string
  stream?: boolean
}

export interface AIQueryResponse {
  answer: string
  source_jobs: string[]
  jobs_found: number
  ai_used: boolean
  model: string
  fallback: boolean
}

export interface AISuggestion {
  suggestions: string[]
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  isStreaming: boolean
  sourceJobs: JobSummary[]
  jobsTotal: number
  aiUsed: boolean
  fallback: boolean
  timestamp: Date
}
